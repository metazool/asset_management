from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from asset_management.assets.serializers import CalibrationCertificateSerializer
from asset_management.users.models import CustomUser


class CalibrationCertificateSerializerTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpass123", username="testuser"
        )
        self.valid_data = {
            "certificate_number": "CERT-001",
            "version": "1.0",
            "status": "DRAFT",
            "issue_date": "2024-01-01",
            "expiry_date": "2024-12-31",
            "certificate_type": "ROUTINE",
            "created_by": self.user.id,
            "calibration_data": {
                "standard_used": "NIST Standard",
                "uncertainty": "0.1",
                "temperature": {
                    "measured_values": [20.0, 21.0, 22.0],
                    "reference_values": [20.1, 21.1, 22.1],
                    "correlation_coefficient": 0.99,
                    "uncertainty": "0.2",
                },
                "humidity": {"measured_value": 50.0, "uncertainty": "0.5"},
            },
        }

    def test_valid_data(self):
        """Test serializer with valid data."""
        serializer = CalibrationCertificateSerializer(data=self.valid_data)
        is_valid = serializer.is_valid()
        if not is_valid:
            print("Validation errors:", serializer.errors)
        self.assertTrue(is_valid)
        self.assertEqual(serializer.errors, {})

    def test_invalid_certificate_type(self):
        """Test validation of invalid certificate type."""
        data = self.valid_data.copy()
        data["certificate_type"] = "INVALID"

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("certificate_type", serializer.errors)

    def test_expiry_date_before_issue_date(self):
        """Test validation when expiry date is before issue date."""
        data = self.valid_data.copy()
        data["expiry_date"] = "2023-12-31"

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("expiry_date", serializer.errors)

    def test_expiry_date_same_as_issue_date(self):
        """Test validation when expiry date is same as issue date."""
        data = self.valid_data.copy()
        data["expiry_date"] = "2024-01-01"

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("expiry_date", serializer.errors)

    def test_missing_required_fields(self):
        """Test validation of missing required fields."""
        data = self.valid_data.copy()
        del data["certificate_number"]

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("certificate_number", serializer.errors)

    def test_invalid_calibration_data_structure(self):
        """Test validation of invalid calibration data structure."""
        data = self.valid_data.copy()
        data["calibration_data"] = "invalid"

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("calibration_data", serializer.errors)

    def test_missing_calibration_data_fields(self):
        """Test validation of missing required calibration data fields."""
        data = self.valid_data.copy()
        del data["calibration_data"]["standard_used"]

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("calibration_data", serializer.errors)

    def test_invalid_temperature_data(self):
        """Test validation of invalid temperature data structure."""
        data = self.valid_data.copy()
        data["calibration_data"]["temperature"] = "invalid"

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("calibration_data", serializer.errors)

    def test_invalid_humidity_data(self):
        """Test validation of invalid humidity data structure."""
        data = self.valid_data.copy()
        data["calibration_data"]["humidity"] = "invalid"

        serializer = CalibrationCertificateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("calibration_data", serializer.errors)

    def test_create_certificate(self):
        """Test creating a new calibration certificate."""
        serializer = CalibrationCertificateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        certificate = serializer.save()

        self.assertEqual(certificate.certificate_number, "CERT-001")
        self.assertEqual(certificate.certificate_type, "ROUTINE")

    def test_update_certificate(self):
        """Test updating an existing calibration certificate."""
        # First create a certificate
        serializer = CalibrationCertificateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        certificate = serializer.save()

        # Update the certificate
        update_data = self.valid_data.copy()
        update_data["certificate_number"] = "CERT-002"
        update_data["certificate_type"] = "VERIFICATION"

        update_serializer = CalibrationCertificateSerializer(
            certificate, data=update_data
        )
        self.assertTrue(update_serializer.is_valid())
        updated_certificate = update_serializer.save()

        self.assertEqual(updated_certificate.certificate_number, "CERT-002")
        self.assertEqual(updated_certificate.certificate_type, "VERIFICATION")
