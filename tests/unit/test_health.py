"""Unit tests for health endpoints."""

import json


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "transactbank-api"

    def test_readiness_check(self, client):
        """Should return ready status when DB is connected."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ready"
