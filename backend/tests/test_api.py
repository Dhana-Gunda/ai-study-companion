import pytest
import httpx
from app.main import app
from app.database import init_db

@pytest.mark.asyncio
async def test_root_and_health_endpoints():
    await init_db()
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # Test root endpoint
        res = await client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "online"
        assert "health" in data

        # Test health probe
        health_res = await client.get("/api/health")
        assert health_res.status_code == 200
        health_data = health_res.json()
        assert "database" in health_data
        assert "ollama" in health_data
        assert health_data["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_session_lifecycle():
    await init_db()
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # Create session
        create_res = await client.post("/api/sessions", json={"title": "Test PM Session"})
        assert create_res.status_code == 200
        session_data = create_res.json()
        session_id = session_data["id"]
        assert session_data["title"] == "Test PM Session"

        # Fetch session list
        list_res = await client.get("/api/sessions")
        assert list_res.status_code == 200
        sessions = list_res.json()
        assert any(s["id"] == session_id for s in sessions)

        # Fetch single session
        get_res = await client.get(f"/api/sessions/{session_id}")
        assert get_res.status_code == 200
        detail = get_res.json()
        assert detail["id"] == session_id
        assert "messages" in detail

        # Delete session
        del_res = await client.delete(f"/api/sessions/{session_id}")
        assert del_res.status_code == 200
