from django.contrib import admin
from .models import (
    Location,
    Department,
    Instrument,
    CalibrationCertificate,
    CalibrationRecord,
    Review,
    MaintenanceRecord,
    Site,
    SensorType,
    MeasurementType,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "contact_email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "address")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "room", "site")
    list_filter = ("site", "building")
    search_fields = ("name", "building", "room")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "min_range", "max_range", "accuracy")
    list_filter = ("unit",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(MeasurementType)
class MeasurementTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "standard")
    list_filter = ("standard",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_number", "model", "status", "resolution")
    list_filter = (
        "status",
        "department",
        "location",
        "sensor_types",
        "measurement_types",
    )
    search_fields = ("name", "serial_number", "model", "manufacturer")
    filter_horizontal = ("sensor_types", "measurement_types")


@admin.register(CalibrationCertificate)
class CalibrationCertificateAdmin(admin.ModelAdmin):
    list_display = (
        "certificate_number",
        "version",
        "status",
        "issue_date",
        "expiry_date",
        "created_by",
    )
    list_filter = ("status", "certificate_type", "issue_date")
    search_fields = ("certificate_number",)
    date_hierarchy = "issue_date"


@admin.register(CalibrationRecord)
class CalibrationRecordAdmin(admin.ModelAdmin):
    list_display = (
        "instrument",
        "date_performed",
        "next_calibration_date",
        "status",
        "performed_by",
    )
    list_filter = ("status", "calibration_type")
    search_fields = ("instrument__name", "instrument__serial_number")
    date_hierarchy = "date_performed"


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("instrument", "start_date", "end_date", "status", "performed_by")
    list_filter = ("status", "maintenance_type")
    search_fields = ("instrument__name", "instrument__serial_number")
    date_hierarchy = "start_date"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("instrument", "status", "priority", "requested_by", "assigned_to")
    list_filter = ("status", "priority")
    search_fields = ("instrument__name", "instrument__serial_number", "reason")
