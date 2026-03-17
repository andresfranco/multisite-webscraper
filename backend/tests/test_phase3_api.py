"""Phase 3: Frontend MVP – Backend API integration tests.

Covers the REST endpoints that power the React frontend:
- GET  /api/v1/health
- POST /api/v1/configs/auto-detect  (mocked fetcher)
- GET  /api/v1/configs/
- POST /api/v1/configs/
- GET  /api/v1/configs/{id}
- PUT  /api/v1/configs/{id}
- DELETE /api/v1/configs/{id}
- POST /api/v1/configs/{id}/test   (mocked scraping engine)
- GET  /api/v1/jobs/
- POST /api/v1/jobs/               (mocked Celery)
- GET  /api/v1/jobs/{id}
- POST /api/v1/jobs/{id}/cancel
- GET  /api/v1/results/
- GET  /api/v1/results/stats
- GET  /api/v1/results/export?format=json
- GET  /api/v1/results/export?format=csv
- GET  /api/v1/results/{id}
- DELETE /api/v1/results/{id}
- POST /api/v1/auth/register
- POST /api/v1/auth/login  (happy + error paths)
- GET  /api/v1/schedules/
- POST /api/v1/schedules/          (mocked)
- Pydantic schema validation (ScrapeConfigCreate)
- Security utils: hash/verify password, JWT round-trip, API key generation

All database calls run against the real app using in-memory SQLite (overriding
the default PostgreSQL URL via an env override + ASGITransport).
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
import os

# Override DB URL before importing app so it uses SQLite in-memory
os.environ.setdefault(
    "DATABASE_URL", "sqlite+aiosqlite:///./test_phase3.db"
)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import get_session
from app.models import Base
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from app.schemas.config import ScrapeConfigCreate, FieldConfigSchema

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_phase3.db"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Per-test SQLite DB with tables created; dependency override injected."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# Minimal valid config payload
VALID_CONFIG_PAYLOAD = {
    "name": "Test Config",
    "base_url": "https://example.com",
    "item_selector": "article",
    "fields": [
        {
            "name": "title",
            "selector": "h2",
            "attribute": None,
            "transform": None,
            "required": True,
            "default_value": None,
        }
    ],
    "pagination_type": "none",
    "max_pages": 1,
    "request_delay_ms": 0,
    "use_headless_browser": False,
    "is_active": True,
}


# ===========================================================================
# Health endpoint
# ===========================================================================

class TestHealthEndpoint:
    @pytest.mark.anyio
    async def test_health_returns_200(self, client):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_health_body_has_status(self, client):
        resp = await client.get("/api/v1/health")
        body = resp.json()
        assert body["status"] == "healthy"


# ===========================================================================
# Configs CRUD
# ===========================================================================

class TestConfigsAPI:
    @pytest.mark.anyio
    async def test_list_configs_empty(self, client):
        resp = await client.get("/api/v1/configs/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.anyio
    async def test_create_config_returns_201(self, client):
        resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        assert resp.status_code == 201

    @pytest.mark.anyio
    async def test_create_config_returns_id(self, client):
        resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert isinstance(body["id"], int)

    @pytest.mark.anyio
    async def test_create_config_stores_name(self, client):
        resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        assert resp.json()["name"] == VALID_CONFIG_PAYLOAD["name"]

    @pytest.mark.anyio
    async def test_create_config_stores_domain(self, client):
        resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        assert resp.json()["domain"] == "example.com"

    @pytest.mark.anyio
    async def test_create_config_invalid_url_scheme(self, client):
        bad_payload = {**VALID_CONFIG_PAYLOAD, "base_url": "ftp://example.com"}
        resp = await client.post("/api/v1/configs/", json=bad_payload)
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_create_config_empty_name_fails(self, client):
        bad_payload = {**VALID_CONFIG_PAYLOAD, "name": ""}
        resp = await client.post("/api/v1/configs/", json=bad_payload)
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_create_config_missing_fields_fails(self, client):
        bad_payload = {**VALID_CONFIG_PAYLOAD, "fields": []}
        resp = await client.post("/api/v1/configs/", json=bad_payload)
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_get_config_by_id(self, client):
        create_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/configs/{config_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == config_id

    @pytest.mark.anyio
    async def test_get_config_not_found(self, client):
        resp = await client.get("/api/v1/configs/999999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_update_config(self, client):
        create_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = create_resp.json()["id"]
        resp = await client.put(
            f"/api/v1/configs/{config_id}",
            json={"name": "Updated Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    @pytest.mark.anyio
    async def test_update_config_not_found(self, client):
        resp = await client.put("/api/v1/configs/999999", json={"name": "X"})
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_delete_config(self, client):
        create_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = create_resp.json()["id"]
        del_resp = await client.delete(f"/api/v1/configs/{config_id}")
        assert del_resp.status_code == 200
        get_resp = await client.get(f"/api/v1/configs/{config_id}")
        assert get_resp.status_code == 404

    @pytest.mark.anyio
    async def test_delete_config_not_found(self, client):
        resp = await client.delete("/api/v1/configs/999999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_list_configs_shows_created(self, client):
        await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        resp = await client.get("/api/v1/configs/")
        assert resp.status_code == 200
        names = [c["name"] for c in resp.json()]
        assert VALID_CONFIG_PAYLOAD["name"] in names

    @pytest.mark.anyio
    async def test_test_config_endpoint(self, client):
        create_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = create_resp.json()["id"]
        with patch(
            "app.api.v1.configs.ScrapingEngine",
        ) as MockEngine:
            mock_instance = MagicMock()
            mock_instance.run = AsyncMock(return_value={
                "items": [{"data": {"title": "Test"}, "item_url": None, "source_url": "https://example.com", "content_hash": "abc"}],
                "pages_scraped": 1,
                "items_found": 1,
                "errors": 0,
            })
            MockEngine.return_value = mock_instance
            resp = await client.post(f"/api/v1/configs/{config_id}/test")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "pages_scraped" in body

    @pytest.mark.anyio
    async def test_test_config_not_found(self, client):
        resp = await client.post("/api/v1/configs/999999/test")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_auto_detect_endpoint_unsafe_url(self, client):
        resp = await client.post(
            "/api/v1/configs/auto-detect",
            json={"url": "http://127.0.0.1/"},
        )
        assert resp.status_code == 400

    @pytest.mark.anyio
    async def test_auto_detect_endpoint_fetch_failure(self, client):
        with patch(
            "app.api.v1.configs.fetch_page",
            new=AsyncMock(return_value=None),
        ):
            resp = await client.post(
                "/api/v1/configs/auto-detect",
                json={"url": "https://example.com"},
            )
        assert resp.status_code == 502

    @pytest.mark.anyio
    async def test_auto_detect_endpoint_success(self, client):
        html = """
<html><body>
  <article><h2>Title</h2><a href="/1">link</a></article>
  <article><h2>Title 2</h2><a href="/2">link</a></article>
</body></html>
"""
        with patch(
            "app.api.v1.configs.fetch_page",
            new=AsyncMock(return_value=html),
        ):
            resp = await client.post(
                "/api/v1/configs/auto-detect",
                json={"url": "https://example.com"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert "item_selector" in body
        assert "fields" in body
        assert "confidence" in body
        assert "detected_via" in body


# ===========================================================================
# Jobs API
# ===========================================================================

class TestJobsAPI:
    @pytest.mark.anyio
    async def test_list_jobs_empty(self, client):
        resp = await client.get("/api/v1/jobs/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.anyio
    async def test_create_job_returns_201(self, client):
        # Create a config first
        config_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = config_resp.json()["id"]

        with patch("app.core.tasks.scrape_task.execute_scrape_job") as mock_task:
            mock_task.delay.return_value = MagicMock(id="mock-celery-id")
            resp = await client.post("/api/v1/jobs/", json={"config_id": config_id})
        assert resp.status_code == 201

    @pytest.mark.anyio
    async def test_create_job_config_not_found(self, client):
        resp = await client.post("/api/v1/jobs/", json={"config_id": 999999})
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_get_job_by_id(self, client):
        config_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = config_resp.json()["id"]

        with patch("app.core.tasks.scrape_task.execute_scrape_job") as mock_task:
            mock_task.delay.return_value = MagicMock(id="mock-task")
            job_resp = await client.post("/api/v1/jobs/", json={"config_id": config_id})
        job_id = job_resp.json()["id"]

        get_resp = await client.get(f"/api/v1/jobs/{job_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == job_id

    @pytest.mark.anyio
    async def test_get_job_not_found(self, client):
        resp = await client.get("/api/v1/jobs/999999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_cancel_pending_job(self, client):
        config_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = config_resp.json()["id"]

        with patch("app.core.tasks.scrape_task.execute_scrape_job") as mock_task:
            mock_task.delay.return_value = MagicMock(id="mock-task")
            job_resp = await client.post("/api/v1/jobs/", json={"config_id": config_id})
        job_id = job_resp.json()["id"]

        cancel_resp = await client.post(f"/api/v1/jobs/{job_id}/cancel")
        assert cancel_resp.status_code == 200
        assert "cancel" in cancel_resp.json()["message"].lower()

    @pytest.mark.anyio
    async def test_cancel_completed_job_fails(self, client):
        config_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = config_resp.json()["id"]

        with patch("app.core.tasks.scrape_task.execute_scrape_job") as mock_task:
            mock_task.delay.return_value = MagicMock(id="mock-task")
            job_resp = await client.post("/api/v1/jobs/", json={"config_id": config_id})
        job_id = job_resp.json()["id"]

        # First cancel to put it in "cancelled"
        await client.post(f"/api/v1/jobs/{job_id}/cancel")
        # Second cancel should fail
        cancel_resp = await client.post(f"/api/v1/jobs/{job_id}/cancel")
        assert cancel_resp.status_code == 400

    @pytest.mark.anyio
    async def test_cancel_job_not_found(self, client):
        resp = await client.post("/api/v1/jobs/999999/cancel")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_list_jobs_status_filter(self, client):
        resp = await client.get("/api/v1/jobs/?status=pending")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ===========================================================================
# Results API
# ===========================================================================

class TestResultsAPI:
    @pytest.mark.anyio
    async def test_list_results_empty(self, client):
        resp = await client.get("/api/v1/results/")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert "page" in body
        assert "pages" in body

    @pytest.mark.anyio
    async def test_list_results_pagination_defaults(self, client):
        resp = await client.get("/api/v1/results/")
        body = resp.json()
        assert body["page"] == 1
        assert body["page_size"] == 20

    @pytest.mark.anyio
    async def test_result_stats_endpoint(self, client):
        resp = await client.get("/api/v1/results/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert "total_items" in body
        assert "total_jobs" in body
        assert "total_configs" in body
        assert "items_by_domain" in body
        assert "jobs_by_status" in body

    @pytest.mark.anyio
    async def test_get_result_not_found(self, client):
        resp = await client.get("/api/v1/results/999999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_delete_result_not_found(self, client):
        resp = await client.delete("/api/v1/results/999999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_export_json_endpoint(self, client):
        resp = await client.get("/api/v1/results/export?format=json")
        assert resp.status_code == 200
        assert "json" in resp.headers["content-type"]

    @pytest.mark.anyio
    async def test_export_csv_endpoint(self, client):
        resp = await client.get("/api/v1/results/export?format=csv")
        assert resp.status_code == 200
        assert "csv" in resp.headers["content-type"]

    @pytest.mark.anyio
    async def test_export_invalid_format(self, client):
        resp = await client.get("/api/v1/results/export?format=xml")
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_export_xlsx_endpoint(self, client):
        resp = await client.get("/api/v1/results/export?format=xlsx")
        assert resp.status_code == 200
        assert "spreadsheet" in resp.headers["content-type"] or "xlsx" in resp.headers["content-disposition"]


# ===========================================================================
# Auth API
# ===========================================================================

class TestAuthAPI:
    @pytest.mark.anyio
    async def test_register_creates_user(self, client):
        import uuid
        unique_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "username": f"user_{uuid.uuid4().hex[:8]}",
                "password": "SecurePass123!",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == unique_email
        assert "id" in body

    @pytest.mark.anyio
    async def test_register_duplicate_email_fails(self, client):
        import uuid
        email = f"dup_{uuid.uuid4().hex[:8]}@test.com"
        username_base = uuid.uuid4().hex[:8]
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "username": f"u1_{username_base}", "password": "Pass123!"},
        )
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "username": f"u2_{username_base}", "password": "Pass123!"},
        )
        assert resp.status_code == 409

    @pytest.mark.anyio
    async def test_login_valid_credentials(self, client):
        import uuid
        email = f"login_{uuid.uuid4().hex[:8]}@test.com"
        pwd = "MyPassword99!"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "username": f"login_{uuid.uuid4().hex[:8]}", "password": pwd},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": pwd},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["access_token"] != ""

    @pytest.mark.anyio
    async def test_login_wrong_password(self, client):
        import uuid
        email = f"bad_{uuid.uuid4().hex[:8]}@test.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "username": f"bad_{uuid.uuid4().hex[:8]}", "password": "RealPass99!"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword!"},
        )
        assert resp.status_code == 401

    @pytest.mark.anyio
    async def test_login_nonexistent_user(self, client):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@nowhere.com", "password": "anything"},
        )
        assert resp.status_code == 401

    @pytest.mark.anyio
    async def test_me_endpoint_requires_auth(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)


# ===========================================================================
# Schedules API
# ===========================================================================

class TestSchedulesAPI:
    @pytest.mark.anyio
    async def test_list_schedules_empty(self, client):
        resp = await client.get("/api/v1/schedules")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.anyio
    async def test_get_schedule_not_found(self, client):
        resp = await client.get("/api/v1/schedules/999999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_create_schedule_config_not_found(self, client):
        resp = await client.post(
            "/api/v1/schedules",
            json={
                "name": "My Schedule",
                "config_id": 999999,
                "cron_expression": "0 6 * * *",
                "is_active": True,
            },
        )
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_delete_schedule_not_found(self, client):
        resp = await client.delete("/api/v1/schedules/999999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_create_and_delete_schedule(self, client):
        config_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = config_resp.json()["id"]

        create_resp = await client.post(
            "/api/v1/schedules",
            json={
                "name": "Daily Scrape",
                "config_id": config_id,
                "cron_expression": "0 6 * * *",
                "is_active": True,
            },
        )
        assert create_resp.status_code == 201
        schedule_id = create_resp.json()["id"]

        del_resp = await client.delete(f"/api/v1/schedules/{schedule_id}")
        assert del_resp.status_code == 204

    @pytest.mark.anyio
    async def test_update_schedule(self, client):
        config_resp = await client.post("/api/v1/configs/", json=VALID_CONFIG_PAYLOAD)
        config_id = config_resp.json()["id"]

        create_resp = await client.post(
            "/api/v1/schedules",
            json={
                "name": "Weekly Scrape",
                "config_id": config_id,
                "cron_expression": "0 6 * * 1",
                "is_active": True,
            },
        )
        schedule_id = create_resp.json()["id"]

        update_resp = await client.patch(
            f"/api/v1/schedules/{schedule_id}",
            json={"is_active": False},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["is_active"] is False


# ===========================================================================
# Security utilities
# ===========================================================================

class TestSecurityUtils:
    def test_hash_password_returns_string(self):
        h = hash_password("mypassword")
        assert isinstance(h, str)
        assert len(h) > 20

    def test_verify_password_correct(self):
        h = hash_password("mypassword")
        assert verify_password("mypassword", h) is True

    def test_verify_password_wrong(self):
        h = hash_password("mypassword")
        assert verify_password("wrongpassword", h) is False

    def test_create_access_token_returns_string(self):
        token = create_access_token(subject=42)
        assert isinstance(token, str)
        assert len(token) > 10

    def test_decode_access_token_round_trip(self):
        token = create_access_token(subject=42)
        subject = decode_access_token(token)
        assert subject == "42"

    def test_decode_invalid_token_returns_none(self):
        result = decode_access_token("not.a.valid.token")
        assert result is None

    def test_generate_api_key_length(self):
        key = generate_api_key()
        assert len(key) == 64  # 32 bytes = 64 hex chars

    def test_generate_api_key_is_unique(self):
        keys = {generate_api_key() for _ in range(20)}
        assert len(keys) == 20

    def test_generate_api_key_is_hex(self):
        key = generate_api_key()
        int(key, 16)  # Should not raise


# ===========================================================================
# Pydantic schema validation
# ===========================================================================

class TestPydanticSchemas:
    def test_valid_scrape_config_create(self):
        config = ScrapeConfigCreate(
            name="Test",
            base_url="https://example.com",
            item_selector="article",
            fields=[
                FieldConfigSchema(name="title", selector="h2")
            ],
        )
        assert config.name == "Test"
        assert config.domain == "example.com"

    def test_invalid_scheme_raises(self):
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ScrapeConfigCreate(
                name="Test",
                base_url="ftp://example.com",
                item_selector="article",
                fields=[FieldConfigSchema(name="title", selector="h2")],
            )

    def test_no_netloc_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ScrapeConfigCreate(
                name="Test",
                base_url="https://",
                item_selector="article",
                fields=[FieldConfigSchema(name="title", selector="h2")],
            )

    def test_pagination_type_enum_valid(self):
        config = ScrapeConfigCreate(
            name="Test",
            base_url="https://example.com",
            item_selector="article",
            fields=[FieldConfigSchema(name="title", selector="h2")],
            pagination_type="next_link",
        )
        assert config.pagination_type == "next_link"

    def test_pagination_type_invalid_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ScrapeConfigCreate(
                name="Test",
                base_url="https://example.com",
                item_selector="article",
                fields=[FieldConfigSchema(name="title", selector="h2")],
                pagination_type="invalid_type",
            )

    def test_max_pages_minimum(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ScrapeConfigCreate(
                name="Test",
                base_url="https://example.com",
                item_selector="article",
                fields=[FieldConfigSchema(name="title", selector="h2")],
                max_pages=0,
            )

    def test_request_delay_ms_bounds(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ScrapeConfigCreate(
                name="Test",
                base_url="https://example.com",
                item_selector="article",
                fields=[FieldConfigSchema(name="title", selector="h2")],
                request_delay_ms=-1,
            )
