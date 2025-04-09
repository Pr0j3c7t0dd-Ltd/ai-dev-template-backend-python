"""
Functional tests for the health endpoint.
"""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient


@pytest.mark.functional
def test_health_endpoint_returns_200(test_client: TestClient):
    """Test that the health endpoint returns a 200 status code."""
    response = test_client.get("/api/v1/health")
    assert response.status_code == HTTPStatus.OK


@pytest.mark.functional
def test_health_endpoint_returns_valid_json(test_client: TestClient):
    """Test that the health endpoint returns valid JSON with the expected structure."""
    response = test_client.get("/api/v1/health")
    data = response.json()

    # Check the structure of the response
    assert "status" in data
    assert "details" in data
    assert "database" in data["details"]
    assert "services" in data["details"]


@pytest.mark.functional
def test_health_endpoint_database_status(test_client: TestClient):
    """Test that the health endpoint returns a valid database status."""
    response = test_client.get("/api/v1/health")
    data = response.json()

    # In tests, the database status should be one of these values
    assert data["details"]["database"] in ["connected", "error"]

    # If database is connected, the overall status should be healthy
    if data["details"]["database"] == "connected":
        assert data["status"] == "healthy"

    # If database has an error, the overall status should be unhealthy
    if data["details"]["database"] == "error":
        assert data["status"] == "unhealthy"


@pytest.mark.functional
def test_health_endpoint_services_status(test_client: TestClient):
    """Test that the health endpoint returns a valid services status."""
    response = test_client.get("/api/v1/health")
    data = response.json()

    # Services should be operational
    assert data["details"]["services"] == "operational"
