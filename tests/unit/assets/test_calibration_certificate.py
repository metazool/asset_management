import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from asset_management.assets.models import CalibrationCertificate
from asset_management.users.models import CustomUser


@pytest.mark.unit
def test_validate_correlation_data_valid():
    """Test validation of valid correlation data."""
    cert = CalibrationCertificate()
    cert.calibration_data = {
        "temperature": {
            "measured_values": [20.1, 25.2, 30.3],
            "reference_values": [20.0, 25.0, 30.0],
            "correlation_coefficient": 0.999,
            "uncertainty": 0.1,
        }
    }
    is_valid, message = cert.validate_correlation_data()
    assert is_valid
    assert message == "Validation successful"


@pytest.mark.unit
def test_validate_correlation_data_missing_fields():
    """Test validation of correlation data with missing fields."""
    cert = CalibrationCertificate()
    cert.calibration_data = {
        "temperature": {
            "measured_values": [20.1, 25.2, 30.3],
            "reference_values": [20.0, 25.0, 30.0],
            # Missing correlation_coefficient and uncertainty
        }
    }
    is_valid, message = cert.validate_correlation_data()
    assert not is_valid
    assert "Missing required field" in message


@pytest.mark.unit
def test_validate_correlation_data_mismatched_lengths():
    """Test validation of correlation data with mismatched array lengths."""
    cert = CalibrationCertificate()
    cert.calibration_data = {
        "temperature": {
            "measured_values": [20.1, 25.2],  # Only 2 values
            "reference_values": [20.0, 25.0, 30.0],  # 3 values
            "correlation_coefficient": 0.999,
            "uncertainty": 0.1,
        }
    }
    is_valid, message = cert.validate_correlation_data()
    assert not is_valid
    assert "must have the same length" in message


@pytest.mark.unit
def test_validate_acceptance_criteria_valid():
    """Test validation of valid acceptance criteria."""
    cert = CalibrationCertificate()
    cert.calibration_data = {
        "temperature": {
            "measured_values": [20.1, 25.2, 30.3],
            "reference_values": [20.0, 25.0, 30.0],
            "correlation_coefficient": 0.999,
            "uncertainty": 0.1,
        }
    }
    cert.acceptance_criteria = {
        "temperature": {"tolerance": 0.5, "correlation_threshold": 0.99}
    }
    is_valid, message = cert.validate_acceptance_criteria()
    assert is_valid
    assert message == "All acceptance criteria met"


@pytest.mark.unit
def test_validate_acceptance_criteria_exceeds_tolerance():
    """Test validation when measurements exceed tolerance."""
    cert = CalibrationCertificate()
    cert.calibration_data = {
        "temperature": {
            "measured_values": [20.6],  # Exceeds tolerance of 0.5
            "reference_values": [20.0],
            "correlation_coefficient": 0.999,
            "uncertainty": 0.1,
        }
    }
    cert.acceptance_criteria = {"temperature": {"tolerance": 0.5}}
    is_valid, message = cert.validate_acceptance_criteria()
    assert not is_valid
    assert "exceeds tolerance" in message


@pytest.mark.unit
def test_validate_acceptance_criteria_below_correlation_threshold():
    """Test validation when correlation coefficient is below threshold."""
    cert = CalibrationCertificate()
    cert.calibration_data = {
        "temperature": {
            "measured_values": [20.1, 25.2, 30.3],
            "reference_values": [20.0, 25.0, 30.0],
            "correlation_coefficient": 0.98,  # Below threshold of 0.99
            "uncertainty": 0.1,
        }
    }
    cert.acceptance_criteria = {"temperature": {"correlation_threshold": 0.99}}
    is_valid, message = cert.validate_acceptance_criteria()
    assert not is_valid
    assert "below threshold" in message


@pytest.mark.unit
def test_add_qa_review():
    """Test adding a QA review to a certificate."""
    user = CustomUser.objects.create_user(
        username="test_user", email="test@example.com", password="testpass123"
    )
    cert = CalibrationCertificate.objects.create(
        certificate_number="CERT-001",
        version=1,
        status=CalibrationCertificate.DRAFT,
        issue_date=timezone.now().date(),
        expiry_date=(timezone.now() + timedelta(days=365)).date(),
        certificate_type="ROUTINE",
        created_by=user,
        calibration_data={"standard_used": "Test Standard", "uncertainty": 0.1},
    )
    reviewer = CustomUser.objects.create_user(
        username="qa_user", email="qa_user@example.com", password="testpass123"
    )
    cert.add_qa_review(
        reviewer=reviewer,
        status="APPROVED",
        comments="All measurements within tolerance",
        non_conformities=[
            {
                "parameter": "temperature",
                "issue": "Minor deviation",
                "severity": "minor",
            }
        ],
        corrective_actions=[
            {"action": "Repeated measurement", "result": "Within tolerance"}
        ],
    )
    cert.refresh_from_db()
    assert cert.reviewer == reviewer
    assert cert.review_notes == "All measurements within tolerance"
    assert cert.status == cert.APPROVED
    assert len(cert.non_conformities) == 1
    assert len(cert.corrective_actions) == 1


@pytest.mark.unit
def test_create_new_version():
    """Test creating a new version of a certificate."""
    user = CustomUser.objects.create_user(
        username="test_user", email="test@example.com", password="testpass123"
    )
    original = CalibrationCertificate.objects.create(
        certificate_number="CERT-001",
        version=1,
        status=CalibrationCertificate.APPROVED,
        issue_date=timezone.now().date(),
        expiry_date=(timezone.now() + timedelta(days=365)).date(),
        certificate_type="ROUTINE",
        created_by=user,
        calibration_data={"standard_used": "Test Standard", "uncertainty": 0.1},
    )

    new_version = original.create_new_version()

    assert new_version.certificate_number == "CERT-001"
    assert new_version.version == 2
    assert new_version.status == CalibrationCertificate.DRAFT

    # Check that original is now superseded
    original.refresh_from_db()
    assert original.status == CalibrationCertificate.SUPERSEDED
