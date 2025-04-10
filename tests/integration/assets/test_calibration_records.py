import pytest
from datetime import datetime, timedelta
from rest_framework import status
from django.utils import timezone
from asset_management.assets.models import (
    CalibrationCertificate,
    CalibrationRecord,
    Instrument,
)
from asset_management.users.models import CustomUser as User


@pytest.mark.integration
@pytest.mark.django_db
def test_create_calibration_record(api_client, admin_user, instrument, db):
    """Test creating a new calibration record with certificate."""
    api_client.force_authenticate(user=admin_user)

    # First create a certificate
    cert_data = {
        "certificate_number": "CERT-001",
        "certificate_type": "ROUTINE",
        "issue_date": timezone.now().date().isoformat(),
        "expiry_date": (timezone.now() + timedelta(days=365)).date().isoformat(),
        "created_by": admin_user.id,
        "calibration_data": {
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
            "temperature": {
                "measured_values": [20.1, 25.2, 30.3],
                "reference_values": [20.0, 25.0, 30.0],
                "correlation_coefficient": 0.999,
                "uncertainty": 0.1,
            },
            "humidity": {"measured_value": 45.0, "uncertainty": 2.0},
        },
    }
    cert_response = api_client.post(
        "/api/calibration-certificates/", cert_data, format="json"
    )
    assert cert_response.status_code == status.HTTP_201_CREATED
    certificate = CalibrationCertificate.objects.get(id=cert_response.data["id"])

    # Create calibration record
    record_data = {
        "instrument": instrument.id,
        "certificate": certificate.id,
        "date_performed": timezone.now().isoformat(),
        "next_calibration_date": (timezone.now() + timedelta(days=365)).isoformat(),
        "calibration_type": "routine",
        "description": "Initial calibration",
        "status": "completed",
        "performed_by": admin_user.id,
    }
    response = api_client.post("/api/calibration-records/", record_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert CalibrationRecord.objects.count() == 1
    record = CalibrationRecord.objects.first()
    assert record.instrument == instrument
    assert record.certificate == certificate
    assert record.performed_by == admin_user


@pytest.mark.integration
@pytest.mark.django_db
def test_update_calibration_record(api_client, admin_user, instrument, db):
    """Test updating an existing calibration record."""
    api_client.force_authenticate(user=admin_user)

    # Create a certificate first
    certificate = CalibrationCertificate.objects.create(
        certificate_number="CERT-002",
        certificate_type="ROUTINE",
        issue_date=timezone.now().date(),
        expiry_date=(timezone.now() + timedelta(days=365)).date(),
        created_by=admin_user,
        calibration_data={
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
        },
    )

    # Create initial record
    record = CalibrationRecord.objects.create(
        instrument=instrument,
        certificate=certificate,
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
        performed_by=admin_user,
        calibration_type="routine",
        description="Initial calibration",
        status="completed",
    )

    # Update record
    update_data = {
        "description": "Updated description after verification",
        "status": "completed",
    }
    response = api_client.patch(
        f"/api/calibration-records/{record.id}/", update_data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    record.refresh_from_db()
    assert record.description == "Updated description after verification"
    assert record.status == "completed"


@pytest.mark.integration
@pytest.mark.django_db
def test_calibration_record_validation(api_client, admin_user, instrument, db):
    """Test validation rules for calibration records."""
    api_client.force_authenticate(user=admin_user)

    # Test invalid date range
    invalid_data = {
        "instrument": instrument.id,
        "date_performed": timezone.now().isoformat(),
        "next_calibration_date": (
            timezone.now() - timedelta(days=1)
        ).isoformat(),  # Invalid: next_calibration_date before date_performed
        "calibration_type": "routine",
        "description": "Test calibration",
        "status": "scheduled",
        "performed_by": admin_user.id,
    }
    response = api_client.post("/api/calibration-records/", invalid_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "next_calibration_date" in str(response.data)


@pytest.mark.integration
@pytest.mark.django_db
def test_calibration_record_permissions(
    api_client, admin_user, regular_user, instrument, db
):
    """Test permissions for calibration record operations."""
    # Create a certificate first
    certificate = CalibrationCertificate.objects.create(
        certificate_number="CERT-003",
        certificate_type="ROUTINE",
        issue_date=timezone.now().date(),
        expiry_date=(timezone.now() + timedelta(days=365)).date(),
        created_by=admin_user,
        calibration_data={
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
        },
    )

    # Create a record as admin
    api_client.force_authenticate(user=admin_user)
    record = CalibrationRecord.objects.create(
        instrument=instrument,
        certificate=certificate,
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
        performed_by=admin_user,
        calibration_type="routine",
        description="Test calibration",
        status="completed",
    )

    # Regular user should not be able to update
    api_client.force_authenticate(user=regular_user)
    update_data = {"description": "Unauthorized update"}
    response = api_client.patch(
        f"/api/calibration-records/{record.id}/", update_data, format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Regular user should be able to view
    response = api_client.get(f"/api/calibration-records/{record.id}/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.django_db
def test_calibration_record_certificate_relationship(
    api_client, admin_user, instrument, db
):
    """Test the relationship between calibration records and certificates."""
    api_client.force_authenticate(user=admin_user)

    # Create a certificate
    cert_data = {
        "certificate_number": "CERT-004",
        "certificate_type": "ROUTINE",
        "issue_date": timezone.now().date().isoformat(),
        "expiry_date": (timezone.now() + timedelta(days=365)).date().isoformat(),
        "created_by": admin_user.id,
        "calibration_data": {
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
            "temperature": {
                "measured_values": [20.1, 25.2, 30.3],
                "reference_values": [20.0, 25.0, 30.0],
                "correlation_coefficient": 0.999,
                "uncertainty": 0.1,
            },
            "humidity": {"measured_value": 45.0, "uncertainty": 2.0},
        },
    }
    cert_response = api_client.post(
        "/api/calibration-certificates/", cert_data, format="json"
    )
    assert cert_response.status_code == status.HTTP_201_CREATED
    certificate = CalibrationCertificate.objects.get(id=cert_response.data["id"])

    # Create record with certificate
    record_data = {
        "instrument": instrument.id,
        "certificate": certificate.id,
        "date_performed": timezone.now().isoformat(),
        "next_calibration_date": (timezone.now() + timedelta(days=365)).isoformat(),
        "calibration_type": "routine",
        "description": "Test calibration",
        "status": "completed",
        "performed_by": admin_user.id,
    }
    response = api_client.post("/api/calibration-records/", record_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    record = CalibrationRecord.objects.get(id=response.data["id"])
    assert record.certificate == certificate
    assert certificate.calibration_records.count() == 1
    assert certificate.calibration_records.first() == record


@pytest.mark.integration
@pytest.mark.django_db
def test_calibration_record_filtering(api_client, admin_user, instrument, db):
    """Test filtering calibration records by various criteria."""
    api_client.force_authenticate(user=admin_user)

    # Create a certificate first
    certificate = CalibrationCertificate.objects.create(
        certificate_number="CERT-005",
        certificate_type="ROUTINE",
        issue_date=timezone.now().date(),
        expiry_date=(timezone.now() + timedelta(days=365)).date(),
        created_by=admin_user,
        calibration_data={
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
        },
    )

    # Create multiple records with different statuses
    CalibrationRecord.objects.create(
        instrument=instrument,
        certificate=certificate,
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
        performed_by=admin_user,
        calibration_type="routine",
        description="Routine calibration",
        status="completed",
    )

    CalibrationRecord.objects.create(
        instrument=instrument,
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
        performed_by=admin_user,
        calibration_type="special",
        description="Special calibration",
        status="scheduled",
    )

    # Test filtering by status
    response = api_client.get("/api/calibration-records/?status=completed")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["status"] == "completed"

    # Test filtering by calibration type
    response = api_client.get("/api/calibration-records/?calibration_type=special")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["calibration_type"] == "special"


@pytest.mark.integration
@pytest.mark.django_db
def test_calibration_record_status_transitions(api_client, admin_user, instrument, db):
    """Test valid and invalid status transitions for calibration records."""
    api_client.force_authenticate(user=admin_user)

    # Create a certificate first
    certificate = CalibrationCertificate.objects.create(
        certificate_number="CERT-006",
        certificate_type="ROUTINE",
        issue_date=timezone.now().date(),
        expiry_date=(timezone.now() + timedelta(days=365)).date(),
        created_by=admin_user,
        calibration_data={
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
        },
    )

    # Create initial record
    record = CalibrationRecord.objects.create(
        instrument=instrument,
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
        performed_by=admin_user,
        calibration_type="routine",
        description="Test calibration",
        status="scheduled",
    )

    # Test valid transition: scheduled -> in_progress
    response = api_client.patch(
        f"/api/calibration-records/{record.id}/",
        {"status": "in_progress"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    record.refresh_from_db()
    assert record.status == "in_progress"

    # Test valid transition: in_progress -> completed (with certificate)
    response = api_client.patch(
        f"/api/calibration-records/{record.id}/",
        {"status": "completed", "certificate": certificate.id},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    record.refresh_from_db()
    assert record.status == "completed"
    assert record.certificate == certificate

    # Test invalid transition: completed -> in_progress
    response = api_client.patch(
        f"/api/calibration-records/{record.id}/",
        {"status": "in_progress"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "status" in str(response.data)


@pytest.mark.integration
@pytest.mark.django_db
def test_calibration_record_search(api_client, admin_user, instrument, db):
    """Test searching calibration records by description."""
    api_client.force_authenticate(user=admin_user)

    # Create a certificate first
    certificate = CalibrationCertificate.objects.create(
        certificate_number="CERT-007",
        certificate_type="ROUTINE",
        issue_date=timezone.now().date(),
        expiry_date=(timezone.now() + timedelta(days=365)).date(),
        created_by=admin_user,
        calibration_data={
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
        },
    )

    # Create records with different descriptions
    CalibrationRecord.objects.create(
        instrument=instrument,
        certificate=certificate,
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
        performed_by=admin_user,
        calibration_type="routine",
        description="Annual calibration check",
        status="completed",
    )

    CalibrationRecord.objects.create(
        instrument=instrument,
        date_performed=timezone.now(),
        next_calibration_date=timezone.now() + timedelta(days=365),
        performed_by=admin_user,
        calibration_type="routine",
        description="Monthly verification",
        status="scheduled",
    )

    # Test search by description
    response = api_client.get("/api/calibration-records/?search=Annual")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert "Annual" in response.data["results"][0]["description"]

    response = api_client.get("/api/calibration-records/?search=Monthly")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert "Monthly" in response.data["results"][0]["description"]
