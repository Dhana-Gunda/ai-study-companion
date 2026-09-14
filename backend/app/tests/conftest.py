import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.core.database import init_db

@pytest_asyncio.fixture(scope="session")
async def app_instance():
    app = create_app()
    await init_db()
    return app

@pytest_asyncio.fixture
async def async_client(app_instance):
    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
