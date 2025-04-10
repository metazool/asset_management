import pytest
from datetime import datetime, timedelta
from rest_framework import status
from django.utils import timezone
from django.test import TestCase
from asset_management.assets.models import (
    CalibrationCertificate,
    CalibrationRecord,
    Instrument,
)
from asset_management.users.models import CustomUser as User
from rest_framework.test import APIClient


class CalibrationCertificateTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
        )
        self.qa_user = User.objects.create_user(
            username="qa",
            email="qa@example.com",
            password="testpass123",
            first_name="QA",
            last_name="User",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="regular",
            email="user@example.com",
            password="testpass123",
            first_name="Regular",
            last_name="User",
        )
        self.client.force_authenticate(user=self.admin_user)

        # Default calibration data for tests
        self.default_calibration_data = {
            "standard_used": "Reference Standard XYZ-123",
            "uncertainty": 0.1,
            "temperature": {
                "measured_values": [20.1, 25.2, 30.3],
                "reference_values": [20.0, 25.0, 30.0],
                "correlation_coefficient": 0.999,
                "uncertainty": 0.1,
            },
            "humidity": {"measured_value": 45.0, "uncertainty": 2.0},
        }

    def test_create_calibration_certificate(self):
        """Test creating a new calibration certificate."""
        data = {
            "certificate_number": "CERT-001",
            "certificate_type": "ROUTINE",
            "issue_date": timezone.now().date().isoformat(),
            "expiry_date": (timezone.now() + timedelta(days=365)).date().isoformat(),
            "created_by": self.admin_user.id,
            "non_conformities": [],
            "calibration_data": self.default_calibration_data,
        }

        response = self.client.post(
            "/api/calibration-certificates/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["certificate_number"], "CERT-001")
        self.assertEqual(response.data["status"], "DRAFT")
        self.assertEqual(response.data["certificate_type"], "ROUTINE")
        self.assertEqual(response.data["version"], 1)

    def test_update_calibration_certificate(self):
        """Test updating a calibration certificate."""
        cert = CalibrationCertificate.objects.create(
            certificate_number="CERT-001",
            certificate_type="ROUTINE",
            issue_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365)).date(),
            created_by=self.admin_user,
            status=CalibrationCertificate.DRAFT,
            calibration_data=self.default_calibration_data,
        )

        update_data = {
            "certificate_type": "POST_REPAIR",
            "calibration_data": {
                "standard_used": "Updated Standard",
                "uncertainty": 0.2,
                "temperature": {
                    "measured_values": [21.0, 26.0, 31.0],
                    "reference_values": [21.0, 26.0, 31.0],
                    "correlation_coefficient": 0.998,
                    "uncertainty": 0.15,
                },
                "humidity": {"measured_value": 50.0, "uncertainty": 2.5},
            },
        }

        response = self.client.patch(
            f"/api/calibration-certificates/{cert.id}/", update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cert.refresh_from_db()
        self.assertEqual(cert.certificate_type, "POST_REPAIR")

    def test_add_qa_review(self):
        """Test adding a QA review to a calibration certificate."""
        cert = CalibrationCertificate.objects.create(
            certificate_number="CERT-001",
            certificate_type="ROUTINE",
            issue_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365)).date(),
            created_by=self.admin_user,
            status=CalibrationCertificate.DRAFT,
            calibration_data=self.default_calibration_data,
        )

        self.client.force_authenticate(user=self.qa_user)
        review_data = {
            "is_approved": True,
            "review_notes": "All measurements within tolerance",
        }

        response = self.client.post(
            f"/api/calibration-certificates/{cert.id}/review/",
            review_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cert.refresh_from_db()
        self.assertEqual(cert.status, CalibrationCertificate.APPROVED)

    def test_create_new_version(self):
        """Test creating a new version of a calibration certificate."""
        cert = CalibrationCertificate.objects.create(
            certificate_number="CERT-001",
            certificate_type="ROUTINE",
            issue_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365)).date(),
            created_by=self.admin_user,
            status=CalibrationCertificate.APPROVED,
            calibration_data=self.default_calibration_data,
        )

        response = self.client.post(
            f"/api/calibration-certificates/{cert.id}/create_version/"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["certificate_number"], "CERT-001")
        self.assertEqual(response.data["version"], 2)

    def test_certificate_validation(self):
        """Test validation of calibration certificate data."""
        data = {
            "certificate_number": "CERT-001",
            "certificate_type": "INVALID_TYPE",
            "issue_date": timezone.now().date().isoformat(),
            "expiry_date": timezone.now().date().isoformat(),
            "created_by": self.admin_user.id,
            "calibration_data": self.default_calibration_data,
        }

        response = self.client.post(
            "/api/calibration-certificates/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("certificate_type", response.data)
        self.assertIn("expiry_date", response.data)

    def test_certificate_permissions(self):
        """Test permissions for calibration certificate operations."""
        cert = CalibrationCertificate.objects.create(
            certificate_number="CERT-001",
            certificate_type="ROUTINE",
            issue_date=timezone.now().date(),
            expiry_date=(timezone.now() + timedelta(days=365)).date(),
            created_by=self.admin_user,
            status=CalibrationCertificate.DRAFT,
            calibration_data=self.default_calibration_data,
        )

        # Test regular user cannot create certificate
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "certificate_number": "CERT-002",
            "certificate_type": "ROUTINE",
            "issue_date": timezone.now().date().isoformat(),
            "expiry_date": (timezone.now() + timedelta(days=365)).date().isoformat(),
            "created_by": self.regular_user.id,
            "calibration_data": self.default_calibration_data,
        }

        response = self.client.post(
            "/api/calibration-certificates/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test regular user cannot update certificate
        update_data = {"certificate_type": "POST_REPAIR"}
        response = self.client.patch(
            f"/api/calibration-certificates/{cert.id}/", update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test regular user cannot review certificate
        review_data = {"is_approved": True, "review_notes": "Test review"}
        response = self.client.post(
            f"/api/calibration-certificates/{cert.id}/review/",
            review_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
