import pytest
from httpx import ASGITransport, AsyncClient
from services.catalog.app import app

@pytest.mark.asyncio
async def test_catalog_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
