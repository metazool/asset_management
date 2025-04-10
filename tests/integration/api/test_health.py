import pytest
from rest_framework import status


@pytest.mark.integration
def test_health_endpoint(api_client):
    response = api_client.get("/api/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}
