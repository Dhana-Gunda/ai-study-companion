import pytest

@pytest.mark.asyncio
async def test_health_check_endpoint(async_client):
    response = await async_client.get("/api/v1/health")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]
