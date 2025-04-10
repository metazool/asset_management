from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Site(models.Model):
    """
    Represents a physical location where instruments are used or stored.
    """

    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_sites",
    )
    code = models.CharField(max_length=10, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Location(models.Model):
    name = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    room = models.CharField(max_length=100)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name="locations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.building}, {self.room})"


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class SensorType(models.Model):
    """
    Represents different types of sensors that can be used in instruments.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(
        max_length=20, help_text="Unit of measurement (e.g., °C, Pa, V)"
    )
    min_range = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Minimum measurement range",
    )
    max_range = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Maximum measurement range",
    )
    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Accuracy as percentage",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.unit})"

    def clean(self):
        """Validate the sensor type data."""
        if self.min_range is not None and self.max_range is not None:
            if self.min_range >= self.max_range:
                raise ValidationError("Minimum range must be less than maximum range")
        super().clean()


class MeasurementType(models.Model):
    """
    Represents different types of measurements that can be performed by instruments.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    standard = models.CharField(
        max_length=100,
        blank=True,
        help_text="Standard or protocol used (e.g., ISO, ASTM)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Issue(models.Model):
    """
    Represents an issue or problem with an instrument.
    """

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    instrument = models.ForeignKey(
        "Instrument", on_delete=models.CASCADE, related_name="issues"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_issues",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_issues",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Instrument(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("maintenance", "Under Maintenance"),
        ("calibration", "Under Calibration"),
    ]

    REVIEW_STATUS_CHOICES = [
        ("none", "No Review Required"),
        ("pending", "Review Pending"),
        ("in_progress", "Review In Progress"),
        ("completed", "Review Completed"),
    ]

    CATEGORY_CHOICES = [
        ("measurement", "Measurement"),
        ("testing", "Testing"),
        ("analysis", "Analysis"),
        ("calibration", "Calibration"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    review_status = models.CharField(
        max_length=20, choices=REVIEW_STATUS_CHOICES, default="none"
    )
    last_review_date = models.DateTimeField(null=True, blank=True)
    next_review_date = models.DateTimeField(null=True, blank=True)
    sensor_types = models.ManyToManyField(
        SensorType,
        related_name="instruments",
        blank=True,
        help_text="Types of sensors installed in the instrument",
    )
    measurement_types = models.ManyToManyField(
        MeasurementType,
        related_name="instruments",
        blank=True,
        help_text="Types of measurements the instrument can perform",
    )
    resolution = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Resolution of the instrument",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    def clean(self):
        """Validate the instrument data."""
        if self.next_review_date and self.last_review_date:
            if self.next_review_date <= self.last_review_date:
                raise ValidationError("Next review date must be after last review date")
        super().clean()


class CalibrationCertificate(models.Model):
    """
    Model for storing calibration certificates.
    """

    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PENDING_REVIEW, "Pending Review"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (SUPERSEDED, "Superseded"),
    ]

    CERTIFICATE_TYPE_CHOICES = [
        ("INITIAL", "Initial Calibration"),
        ("ROUTINE", "Routine Calibration"),
        ("VERIFICATION", "Verification"),
        ("POST_REPAIR", "Post-Repair Calibration"),
    ]

    certificate_number = models.CharField(max_length=50)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPE_CHOICES)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_certificates",
    )
    calibration_data = models.JSONField()
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_certificates",
    )
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    non_conformities = models.JSONField(default=list, blank=True)
    corrective_actions = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["certificate_number", "version"]

    def __str__(self):
        return f"{self.certificate_number} v{self.version}"

    def validate_correlation_data(self):
        """
        Validate the correlation data structure and content.
        Returns a tuple of (is_valid, message).
        """
        if not self.calibration_data:
            return False, "Calibration data is required"

        for parameter, data in self.calibration_data.items():
            required_fields = [
                "measured_values",
                "reference_values",
                "correlation_coefficient",
                "uncertainty",
            ]
            for field in required_fields:
                if field not in data:
                    return (
                        False,
                        f"Missing required field '{field}' for parameter '{parameter}'",
                    )

            if len(data["measured_values"]) != len(data["reference_values"]):
                return (
                    False,
                    "Measured and reference values must have the same length "
                    f"for parameter '{parameter}'",
                )

            if not isinstance(data["correlation_coefficient"], (int, float)):
                return (
                    False,
                    f"Correlation coefficient must be a number for parameter '{parameter}'",
                )

            if not isinstance(data["uncertainty"], (int, float)):
                return (
                    False,
                    f"Uncertainty must be a number for parameter '{parameter}'",
                )

        return True, "Validation successful"

    def validate_acceptance_criteria(self):
        """
        Validate the calibration data against acceptance criteria.
        Returns a tuple of (is_valid, message).
        """
        if not hasattr(self, "acceptance_criteria"):
            return True, "No acceptance criteria defined"

        for parameter, criteria in self.acceptance_criteria.items():
            if parameter not in self.calibration_data:
                return False, f"Parameter '{parameter}' not found in calibration data"

            data = self.calibration_data[parameter]

            # Check tolerance
            if "tolerance" in criteria:
                for measured, reference in zip(
                    data["measured_values"], data["reference_values"]
                ):
                    if abs(measured - reference) > criteria["tolerance"]:
                        return (
                            False,
                            f"Measurement exceeds tolerance for parameter '{parameter}'",
                        )

            # Check correlation threshold
            if "correlation_threshold" in criteria:
                if data["correlation_coefficient"] < criteria["correlation_threshold"]:
                    return (
                        False,
                        f"Correlation coefficient below threshold for parameter '{parameter}'",
                    )

        return True, "All acceptance criteria met"

    def add_qa_review(
        self, reviewer, status, comments, non_conformities=None, corrective_actions=None
    ):
        """
        Add a QA review to the certificate.
        """
        self.reviewer = reviewer
        self.review_date = timezone.now()
        self.review_notes = comments
        self.is_approved = status.lower() == "approved"
        self.status = self.APPROVED if self.is_approved else self.REJECTED

        if non_conformities:
            if not hasattr(self, "non_conformities"):
                self.non_conformities = []
            self.non_conformities.extend(non_conformities)

        if corrective_actions:
            if not hasattr(self, "corrective_actions"):
                self.corrective_actions = []
            self.corrective_actions.extend(corrective_actions)

        self.save()

    def create_new_version(self):
        """
        Create a new version of the certificate.
        """
        new_version = CalibrationCertificate.objects.create(
            certificate_number=self.certificate_number,
            version=self.version + 1,
            status=self.DRAFT,
            issue_date=timezone.now().date(),
            expiry_date=self.expiry_date,
            certificate_type=self.certificate_type,
            created_by=self.created_by,
            calibration_data=self.calibration_data,
        )
        self.status = self.SUPERSEDED
        self.save()
        return new_version


class CalibrationRecord(models.Model):
    CALIBRATION_TYPES = [
        ("routine", "Routine"),
        ("after_repair", "After Repair"),
        ("special", "Special"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="calibration_records"
    )
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    calibration_type = models.CharField(max_length=20, choices=CALIBRATION_TYPES)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    date_performed = models.DateTimeField(null=True, blank=True)
    next_calibration_date = models.DateTimeField()
    certificate = models.ForeignKey(
        CalibrationCertificate,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calibration_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.get_calibration_type_display()} calibration for {self.instrument}"
        )

    def save(self, *args, **kwargs):
        if self.status == "completed" and not self.certificate:
            raise ValueError(
                "A completed calibration must have an associated certificate"
            )
        super().save(*args, **kwargs)

    def clean(self):
        """Validate the calibration record."""
        if (
            self.next_calibration_date
            and self.next_calibration_date <= self.date_performed
        ):
            raise ValidationError(
                "Next calibration date must be after the date performed"
            )
        super().clean()


class Review(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="reviews"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_reviews",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_reviews",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )
    reason = models.TextField()
    external_ticket_id = models.CharField(max_length=100, null=True, blank=True)
    external_ticket_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.instrument} - {self.status}"


class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPES = [
        ("preventive", "Preventive"),
        ("corrective", "Corrective"),
        ("predictive", "Predictive"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="maintenance_records"
    )
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.get_maintenance_type_display()} maintenance for {self.instrument}"
        )
