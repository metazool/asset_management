from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from asset_management.assets.views import (
    InstrumentListView,
    InstrumentDetailView,
    InstrumentCreateView,
    InstrumentUpdateView,
    IssueListView,
    CalibrationRecordView,  # Add these new views
    MaintenanceRecordView,
    CalibrationCertificateView,
)

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="instrument_list"), name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/", include("asset_management.api.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    # Front-end URLs
    path("instruments/", InstrumentListView.as_view(), name="instrument_list"),
    path(
        "instruments/<int:pk>/",
        InstrumentDetailView.as_view(),
        name="instrument_detail",
    ),
    path(
        "instruments/create/", InstrumentCreateView.as_view(), name="instrument_create"
    ),
    path(
        "instruments/<int:pk>/update/",
        InstrumentUpdateView.as_view(),
        name="instrument_update",
    ),
    path(
        "instruments/<int:instrument_id>/issues/",
        IssueListView.as_view(),
        name="issue_list",
    ),
    # New frontend URLs for calibration and maintenance
    path("calibrations/", CalibrationRecordView.as_view(), name="calibration_list"),
    path(
        "calibrations/<int:pk>/",
        CalibrationRecordView.as_view(),
        name="calibration_detail",
    ),
    path("maintenance/", MaintenanceRecordView.as_view(), name="maintenance_list"),
    path(
        "maintenance/<int:pk>/",
        MaintenanceRecordView.as_view(),
        name="maintenance_detail",
    ),
    path(
        "certificates/", CalibrationCertificateView.as_view(), name="certificate_list"
    ),
    path(
        "certificates/<int:pk>/",
        CalibrationCertificateView.as_view(),
        name="certificate_detail",
    ),
    path("", include("asset_management.assets.urls")),
]
