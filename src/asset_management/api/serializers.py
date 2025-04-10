from rest_framework import serializers
from django.utils.dateparse import parse_datetime
from asset_management.assets.models import (
    Location,
    Department,
    Instrument,
    MaintenanceRecord,
    CalibrationRecord,
    CalibrationCertificate,
    Review,
    Site,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = "__all__"


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = "__all__"


class CalibrationRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for CalibrationRecord model with nested relationships.
    """
    performed_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    
    class Meta:
        model = CalibrationRecord
        fields = [
            'id', 'instrument', 'date_performed', 'next_calibration_date',
            'calibration_type', 'status', 'description', 'performed_by',
            'certificate'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        if "date_performed" in data and "next_calibration_date" in data:
            if data["next_calibration_date"] <= data["date_performed"]:
                raise serializers.ValidationError(
                    {
                        "next_calibration_date": "Next calibration date must be after the date performed"
                    }
                )

        # Validate status transitions
        if "status" in data:
            current_status = self.instance.status if self.instance else None
            new_status = data["status"]

            # Allow updates when status isn't changing
            if current_status == new_status:
                return data

            # Define valid transitions
            valid_transitions = {
                "scheduled": ["in_progress", "cancelled"],
                "in_progress": ["completed", "cancelled"],
                "completed": [],  # No valid transitions from completed
                "cancelled": [],  # No valid transitions from cancelled
            }

            if current_status and new_status not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    {
                        "status": f"Invalid status transition from {current_status} to {new_status}"
                    }
                )

            # If transitioning to completed, require a certificate
            if new_status == "completed" and not data.get("certificate"):
                raise serializers.ValidationError(
                    {
                        "certificate": "A certificate is required when completing a calibration"
                    }
                )

        return data

    def validate_next_calibration_date(self, value):
        """
        Validate that next_calibration_date is after date_performed.
        """
        date_performed = self.initial_data.get('date_performed')
        if date_performed:
            date_performed = parse_datetime(date_performed)
            if value <= date_performed:
                raise serializers.ValidationError(
                    "Next calibration date must be after the date performed"
                )
        return value


class CalibrationCertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for CalibrationCertificate model.
    """
    class Meta:
        model = CalibrationCertificate
        fields = [
            'id', 'certificate_number', 'version', 'status', 'issue_date',
            'expiry_date', 'certificate_type', 'created_by', 'calibration_data',
            'reviewer', 'review_date', 'review_notes', 'is_approved',
            'non_conformities', 'corrective_actions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Validate dates
        if 'issue_date' in data and 'expiry_date' in data:
            if data['expiry_date'] <= data['issue_date']:
                raise serializers.ValidationError({
                    'expiry_date': 'Expiry date must be after issue date'
                })

        # Validate calibration data structure
        if 'calibration_data' in data:
            instance = self.instance or CalibrationCertificate(**data)
            is_valid, message = instance.validate_correlation_data()
            if not is_valid:
                raise serializers.ValidationError({
                    'calibration_data': message
                })

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
        )


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("external_ticket_id", "external_ticket_url")


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"
