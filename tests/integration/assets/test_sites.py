import pytest
from datetime import datetime
from rest_framework import status
from asset_management.assets.models import Site, Location
from asset_management.users.models import CustomUser as User


@pytest.mark.integration
@pytest.mark.django_db
def test_create_site(api_client, admin_user, db):
    """Test creating a new site."""
    api_client.force_authenticate(user=admin_user)

    site_data = {
        "name": "Test Site",
        "code": "TS001",
        "address": "123 Test Street",
        "contact_email": "test@example.com",
        "contact_phone": "1234567890",
        "is_active": True,
    }
    response = api_client.post("/api/sites/", site_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Site.objects.count() == 1
    site = Site.objects.first()
    assert site.name == "Test Site"
    assert site.code == "TS001"
    assert site.is_active is True


@pytest.mark.integration
@pytest.mark.django_db
def test_update_site(api_client, admin_user, db):
    """Test updating a site."""
    api_client.force_authenticate(user=admin_user)

    # Create initial site
    site = Site.objects.create(
        name="Initial Site",
        code="IS001",
        address="Initial Address",
        contact_email="initial@example.com",
        contact_phone="0000000000",
        is_active=True,
    )

    # Update site
    update_data = {
        "name": "Updated Site",
        "contact_email": "updated@example.com",
        "is_active": False,
    }
    response = api_client.patch(f"/api/sites/{site.id}/", update_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    site.refresh_from_db()
    assert site.name == "Updated Site"
    assert site.contact_email == "updated@example.com"
    assert site.is_active is False


@pytest.mark.integration
@pytest.mark.django_db
def test_site_validation(api_client, admin_user, db):
    """Test site validation rules."""
    api_client.force_authenticate(user=admin_user)

    # Test with invalid email
    invalid_data = {
        "name": "Test Site",
        "code": "TS001",
        "address": "123 Test Street",
        "contact_email": "invalid-email",
        "contact_phone": "1234567890",
        "is_active": True,
    }
    response = api_client.post("/api/sites/", invalid_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "contact_email" in response.data


@pytest.mark.integration
@pytest.mark.django_db
def test_site_permissions(api_client, admin_user, regular_user, db):
    """Test site permissions."""
    # Create site as admin
    api_client.force_authenticate(user=admin_user)
    site = Site.objects.create(
        name="Test Site",
        code="TS001",
        address="123 Test Street",
        contact_email="test@example.com",
        contact_phone="1234567890",
        is_active=True,
    )

    # Regular user should not be able to update
    api_client.force_authenticate(user=regular_user)
    update_data = {"name": "Unauthorized Update"}
    response = api_client.patch(f"/api/sites/{site.id}/", update_data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Regular user should be able to view
    response = api_client.get(f"/api/sites/{site.id}/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.django_db
def test_site_location_relationship(api_client, admin_user, db):
    """Test the relationship between sites and locations."""
    api_client.force_authenticate(user=admin_user)

    # Create site
    site = Site.objects.create(
        name="Test Site",
        code="TS001",
        address="123 Test Street",
        contact_email="test@example.com",
        contact_phone="1234567890",
        is_active=True,
    )

    # Create location
    location_data = {
        "name": "Test Location",
        "building": "Test Building",
        "room": "Test Room",
        "site": site.id,
    }
    response = api_client.post("/api/locations/", location_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    location = Location.objects.get(id=response.data["id"])
    assert location.site == site
    assert site.locations.count() == 1
    assert site.locations.first() == location
