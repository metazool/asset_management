# Generated by Django 5.0.2 on 2025-04-10 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CalibrationCertificate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("certificate_number", models.CharField(max_length=50)),
                ("version", models.PositiveIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("PENDING_REVIEW", "Pending Review"),
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                            ("SUPERSEDED", "Superseded"),
                        ],
                        default="DRAFT",
                        max_length=20,
                    ),
                ),
                ("issue_date", models.DateField()),
                ("expiry_date", models.DateField()),
                (
                    "certificate_type",
                    models.CharField(
                        choices=[
                            ("INITIAL", "Initial Calibration"),
                            ("ROUTINE", "Routine Calibration"),
                            ("VERIFICATION", "Verification"),
                            ("POST_REPAIR", "Post-Repair Calibration"),
                        ],
                        max_length=20,
                    ),
                ),
                ("calibration_data", models.JSONField()),
                ("review_date", models.DateTimeField(blank=True, null=True)),
                ("review_notes", models.TextField(blank=True)),
                ("is_approved", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CalibrationRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "calibration_type",
                    models.CharField(
                        choices=[
                            ("routine", "Routine"),
                            ("after_repair", "After Repair"),
                            ("special", "Special"),
                        ],
                        max_length=20,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="scheduled",
                        max_length=20,
                    ),
                ),
                ("date_performed", models.DateTimeField(blank=True, null=True)),
                ("next_calibration_date", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=10, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Instrument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("serial_number", models.CharField(max_length=100, unique=True)),
                ("model", models.CharField(max_length=100)),
                ("manufacturer", models.CharField(max_length=100)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("measurement", "Measurement"),
                            ("testing", "Testing"),
                            ("analysis", "Analysis"),
                            ("calibration", "Calibration"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("inactive", "Inactive"),
                            ("maintenance", "Under Maintenance"),
                            ("calibration", "Under Calibration"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                (
                    "review_status",
                    models.CharField(
                        choices=[
                            ("none", "No Review Required"),
                            ("pending", "Review Pending"),
                            ("in_progress", "Review In Progress"),
                            ("completed", "Review Completed"),
                        ],
                        default="none",
                        max_length=20,
                    ),
                ),
                ("last_review_date", models.DateTimeField(blank=True, null=True)),
                ("next_review_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("building", models.CharField(max_length=100)),
                ("room", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="MaintenanceRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "maintenance_type",
                    models.CharField(
                        choices=[
                            ("preventive", "Preventive"),
                            ("corrective", "Corrective"),
                            ("predictive", "Predictive"),
                        ],
                        max_length=20,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="scheduled",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        default="medium",
                        max_length=20,
                    ),
                ),
                ("reason", models.TextField()),
                (
                    "external_ticket_id",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("external_ticket_url", models.URLField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=10, unique=True)),
                ("address", models.TextField()),
                ("contact_email", models.EmailField(max_length=254)),
                ("contact_phone", models.CharField(max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
