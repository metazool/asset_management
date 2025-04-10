from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    Location,
    Department,
    Instrument,
    Review,
    MaintenanceRecord,
    CalibrationRecord,
    CalibrationCertificate,
    Site,
    Issue,
    SensorType,
    MeasurementType,
)
from .services import TicketService

CustomUser = get_user_model()


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class InstrumentSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source="location", write_only=True
    )
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )

    class Meta:
        model = Instrument
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    instrument = InstrumentSerializer(read_only=True)
    instrument_id = serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.all(), source="instrument", write_only=True
    )
    requested_by = serializers.ReadOnlyField(source="requested_by.email")
    assigned_to = serializers.ReadOnlyField(source="assigned_to.email")
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="assigned_to",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "instrument",
            "instrument_id",
            "requested_by",
            "assigned_to",
            "assigned_to_id",
            "status",
            "priority",
            "reason",
            "external_ticket_id",
            "external_ticket_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "requested_by",
            "created_at",
            "updated_at",
            "external_ticket_id",
            "external_ticket_url",
        )

    def create(self, validated_data):
        # Set the requesting user
        validated_data["requested_by"] = self.context["request"].user

        # Create the review
        review = super().create(validated_data)

        # Update instrument review status
        review.instrument.review_status = "pending"
        review.instrument.save()

        # Create external ticket if configured
        ticket_service = TicketService()
        ticket_data = ticket_service.create_ticket(review)
        if ticket_data:
            review.external_ticket_id = ticket_data["ticket_id"]
            review.external_ticket_url = ticket_data["ticket_url"]
            review.save()

        return review

    def update(self, instance, validated_data):
        # Update the review
        review = super().update(instance, validated_data)

        # Update instrument review status based on review status
        if review.status == "completed":
            review.instrument.review_status = "completed"
            review.instrument.last_review_date = review.updated_at
            review.instrument.save()
        elif review.status == "in_progress":
            review.instrument.review_status = "in_progress"
            review.instrument.save()

        # Update external ticket if configured
        ticket_service = TicketService()
        ticket_service.update_ticket(review)

        return review


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    instrument = InstrumentSerializer(read_only=True)
    instrument_id = serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.all(), source="instrument", write_only=True
    )
    performed_by = serializers.ReadOnlyField(source="performed_by.email")

    class Meta:
        model = MaintenanceRecord
        fields = "__all__"
        read_only_fields = ("performed_by", "created_at", "updated_at")


class CalibrationRecordSerializer(serializers.ModelSerializer):
    instrument = InstrumentSerializer(read_only=True)
    instrument_id = serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.all(), source="instrument", write_only=True
    )
    performed_by = serializers.ReadOnlyField(source="performed_by.email")
    certificate = serializers.PrimaryKeyRelatedField(
        queryset=CalibrationCertificate.objects.all(), required=False
    )

    class Meta:
        model = CalibrationRecord
        fields = "__all__"
        read_only_fields = ("performed_by", "created_at", "updated_at")

    def validate(self, data):
        # Validate status transitions
        if self.instance:
            current_status = self.instance.status
            new_status = data.get("status", current_status)

            valid_transitions = {
                "scheduled": ["in_progress", "cancelled"],
                "in_progress": ["completed", "cancelled"],
                "completed": ["cancelled"],
                "cancelled": [],
            }

            if (
                new_status != current_status
                and new_status not in valid_transitions[current_status]
            ):
                raise serializers.ValidationError(
                    {
                        "status": f"Invalid status transition from {current_status} to {new_status}"
                    }
                )

        # Validate completed status requires certificate
        if data.get("status") == "completed" and not data.get("certificate"):
            raise serializers.ValidationError(
                {
                    "certificate": "A completed calibration must have an associated certificate"
                }
            )

        # Validate next_calibration_date is after date_performed
        date_performed = data.get("date_performed")
        next_calibration_date = data.get("next_calibration_date")
        if (
            date_performed
            and next_calibration_date
            and next_calibration_date <= date_performed
        ):
            raise serializers.ValidationError(
                {
                    "next_calibration_date": "Next calibration date must be after date performed"
                }
            )

        return data

    def create(self, validated_data):
        validated_data["performed_by"] = self.context["request"].user
        return super().create(validated_data)


class CalibrationCertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for CalibrationCertificate model.
    """

    created_by = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    certificate_type = serializers.ChoiceField(
        choices=CalibrationCertificate.CERTIFICATE_TYPE_CHOICES
    )
    expiry_date = serializers.DateField()
    calibration_data = serializers.JSONField()

    class Meta:
        model = CalibrationCertificate
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "reviewer", "review_date")

    def validate_expiry_date(self, value):
        """
        Validate that expiry date is after issue date.
        """
        issue_date = self.initial_data.get("issue_date")
        if issue_date and value:
            from django.utils.dateparse import parse_date

            if isinstance(issue_date, str):
                issue_date = parse_date(issue_date)
            if not value > issue_date:
                raise serializers.ValidationError(
                    "Expiry date must be after issue date"
                )
        return value

    def validate_calibration_data(self, value):
        """
        Validate the calibration data structure.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Calibration data must be a dictionary")

        required_fields = ["standard_used", "uncertainty"]
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")

        # Validate temperature data if present
        if "temperature" in value:
            temp_data = value["temperature"]
            if not isinstance(temp_data, dict):
                raise serializers.ValidationError(
                    "Temperature data must be a dictionary"
                )

            temp_required = [
                "measured_values",
                "reference_values",
                "correlation_coefficient",
                "uncertainty",
            ]
            for field in temp_required:
                if field not in temp_data:
                    raise serializers.ValidationError(
                        f"Missing required field in temperature data: {field}"
                    )

            if len(temp_data["measured_values"]) != len(temp_data["reference_values"]):
                raise serializers.ValidationError(
                    "Measured and reference values must have the same length"
                )

        # Validate humidity data if present
        if "humidity" in value:
            humidity_data = value["humidity"]
            if not isinstance(humidity_data, dict):
                raise serializers.ValidationError("Humidity data must be a dictionary")

            humidity_required = ["measured_value", "uncertainty"]
            for field in humidity_required:
                if field not in humidity_data:
                    raise serializers.ValidationError(
                        f"Missing required field in humidity data: {field}"
                    )

        return value

    def validate(self, data):
        """
        Validate the calibration certificate data.
        """
        return data


class IssueSerializer(serializers.ModelSerializer):
    instrument = InstrumentSerializer(read_only=True)
    instrument_id = serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.all(), source="instrument", write_only=True
    )
    reported_by = serializers.ReadOnlyField(source="reported_by.email")
    assigned_to = serializers.ReadOnlyField(source="assigned_to.email")
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="assigned_to",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "instrument",
            "instrument_id",
            "title",
            "description",
            "status",
            "priority",
            "reported_by",
            "assigned_to",
            "assigned_to_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("reported_by", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["reported_by"] = self.context["request"].user
        return super().create(validated_data)


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = "__all__"


class MeasurementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementType
        fields = "__all__"
