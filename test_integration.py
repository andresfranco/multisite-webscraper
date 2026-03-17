import asyncio
import httpx
import uuid

API_BASE = "http://localhost:8000/api/v1"
TEST_EMAIL = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPassword123!"

async def run_integration_test():
    async with httpx.AsyncClient() as client:
        print(f"--- Testing Authentication ---")
        # 1. Register User
        print(f"Registering {TEST_EMAIL}...")
        resp = await client.post(f"{API_BASE}/auth/register", json={
            "email": TEST_EMAIL,
            "username": f"user_{uuid.uuid4().hex[:6]}",
            "password": TEST_PASSWORD
        })
        print("Register Status:", resp.status_code)
        if resp.status_code != 201:
            print("Register failed:", resp.text)
            return
        
        # 2. Login User
        print(f"Logging in...")
        resp = await client.post(f"{API_BASE}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        print("Login Status:", resp.status_code)
        if resp.status_code != 200:
            print("Login failed:", resp.text)
            return
        
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"\n--- Testing Schedules ---")
        # 3. Create a config to schedule
        print("Creating Scrape Config...")
        resp = await client.post(f"{API_BASE}/configs/", json={
            "name": f"Test Config {uuid.uuid4().hex[:4]}",
            "base_url": "https://example.com",
            "item_selector": "article",
            "fields": [
                {"name": "title", "selector": "h1"}
            ]
        }, headers=headers)
        print("Config Creation Status:", resp.status_code)
        if resp.status_code != 201:
            print("Config creation failed:", resp.text)
            return
        config_id = resp.json()["id"]
        
        # 4. Create Schedule
        print("Creating Schedule...")
        resp = await client.post(f"{API_BASE}/schedules", json={
            "name": "Hourly Example Scrape",
            "config_id": config_id,
            "cron_expression": "0 * * * *",
            "is_active": True
        }, headers=headers)
        print("Schedule Creation Status:", resp.status_code)
        if resp.status_code != 201:
            print("Schedule creation failed:", resp.text)
            return
        
        schedule_id = resp.json()["id"]
        
        # 5. List Schedules
        print("Listing Schedules...")
        resp = await client.get(f"{API_BASE}/schedules", headers=headers)
        print("List Schedules Status:", resp.status_code)
        schedules = resp.json()
        print(f"Found {len(schedules)} schedules.")
        if not any(s['id'] == schedule_id for s in schedules):
            print("Created schedule not found in list!")
            return
            
        # 6. Delete Schedule
        print("Deleting Schedule...")
        resp = await client.delete(f"{API_BASE}/schedules/{schedule_id}", headers=headers)
        print("Delete Schedule Status:", resp.status_code)
        
        print("\nAll integration tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
