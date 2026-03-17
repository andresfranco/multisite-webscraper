import structlog
import pytest
from httpx import AsyncClient

log = structlog.get_logger(__name__)


@pytest.mark.anyio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    log.info("testing_health_endpoint")
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
