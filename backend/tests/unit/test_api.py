"""Unit tests — API endpoints (mocked DB)"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

class TestSystemEndpoints:
    @pytest.mark.asyncio
    async def test_health(self):
        import app.database.dependency as dep
        dep.check_db_connection = AsyncMock(return_value=True)
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            await c.get("/health")  # generate at least one observed request
            r = await c.get("/metrics")
        assert r.status_code == 200
        assert "embedhunt_http_requests_total" in r.text

    @pytest.mark.asyncio
    async def test_root(self):
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_company_intelligence_public(self):
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/company/intelligence")
        assert r.status_code == 200
        d = r.json()
        assert d["total_companies"] >= 50 and d["total_portals"] >= 10

    @pytest.mark.asyncio
    async def test_auth_required_for_dashboard(self):
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/dashboard/")
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_required_for_recommendations(self):
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/recommendations/jobs")
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_register_validation(self):
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/register", json={"email":"bad","username":"x","password":"weak","first_name":"A","last_name":"B"})
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_recommendations_with_auth(self):
        from app.auth.jwt import create_access_token
        from app.main import app
        import app.database.session as db_session
        from sqlalchemy.ext.asyncio import AsyncSession

        db_mock = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db_mock.execute = AsyncMock(return_value=mock_result)
        async def override(): yield db_mock
        app.dependency_overrides[db_session.get_db] = override
        token = create_access_token("user-test", "candidate")
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
                r = await c.get("/api/v1/recommendations/jobs", headers={"Authorization": f"Bearer {token}"})
        finally:
            app.dependency_overrides.clear()
        assert r.status_code == 200
        d = r.json()
        assert "total_scanned" in d and "jobs" in d
