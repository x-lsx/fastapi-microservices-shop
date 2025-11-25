import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/users/register", json={"username": "testuser", "password": "testpassword"})
        assert resp.status_code == 200
        user_data = resp.json()
        assert user_data["username"] == "testuser"
        assert "id" in user_data
        assert "is_superuser" in user_data

@pytest.mark.asyncio
async def test_login_user():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/users/register", json={"username": "testuser", "password": "testpassword"})

        resp = await client.post("/auth/login", json={"username": "testuser", "password": "testpassword"})
        assert resp.status_code == 201
        user_data = resp.json()
        assert user_data["username"] == "testuser"
