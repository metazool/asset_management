import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from asset_management.users.models import CustomUser
from asset_management.assets.models import (
    Location,
    Department,
    Instrument,
    MaintenanceRecord,
    CalibrationRecord,
    Site,
)
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.test.utils import setup_databases, teardown_databases

CustomUser = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def admin_user():
    return CustomUser.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
@pytest.mark.django_db
def regular_user():
    return CustomUser.objects.create_user(
        username="regular",
        email="user@example.com",
        password="userpass123",
        first_name="Regular",
        last_name="User",
    )


@pytest.fixture
@pytest.mark.django_db
def qa_user():
    return CustomUser.objects.create_user(
        username="qa",
        email="qa@example.com",
        password="qapass123",
        first_name="QA",
        last_name="User",
        is_staff=True,
    )


@pytest.fixture
def authenticated_client(api_client, regular_user):
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
@pytest.mark.django_db
def site():
    return Site.objects.create(
        name="Test Site",
        code="TEST",
        address="123 Test Street",
        contact_email="test@example.com",
        contact_phone="1234567890",
        is_active=True,
    )


@pytest.fixture
@pytest.mark.django_db
def location(site):
    return Location.objects.create(
        name="Test Location",
        building="Test Building",
        room="Test Room",
        site=site,
    )


@pytest.fixture
@pytest.mark.django_db
def department():
    return Department.objects.create(
        name="Test Department",
        code="TEST",
    )


@pytest.fixture
@pytest.mark.django_db
def instrument(location, department):
    return Instrument.objects.create(
        name="Test Instrument",
        serial_number="TEST123",
        model="Test Model",
        manufacturer="Test Manufacturer",
        location=location,
        department=department,
        status="active",
    )


@pytest.fixture
@pytest.mark.django_db
def maintenance_record(instrument, regular_user):
    return MaintenanceRecord.objects.create(
        instrument=instrument,
        performed_by=regular_user,
        maintenance_type="preventive",
        description="Test maintenance",
        status="completed",
        start_date=timezone.now(),
    )


@pytest.fixture
@pytest.mark.django_db
def calibration_record(instrument, regular_user):
    return CalibrationRecord.objects.create(
        instrument=instrument,
        performed_by=regular_user,
        calibration_type="routine",
        description="Test calibration",
        status="completed",
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
    )


def pytest_configure():
    """Configure pytest for Django."""
    settings.DEBUG = False
    settings.TESTING = True


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the test database."""
    with django_db_blocker.unblock():
        setup_databases(verbosity=1, interactive=False)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass
