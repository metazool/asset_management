from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationViewSet,
    DepartmentViewSet,
    InstrumentViewSet,
    ReviewViewSet,
    MaintenanceRecordViewSet,
    CalibrationRecordViewSet,
    CalibrationCertificateViewSet,
    InstrumentListView,
    InstrumentDetailView,
    InstrumentCreateView,
    InstrumentUpdateView,
    IssueListView,
)

router = DefaultRouter()
router.register(r"locations", LocationViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"instruments", InstrumentViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"maintenance-records", MaintenanceRecordViewSet)
router.register(r"calibration-records", CalibrationRecordViewSet)
router.register(
    r"calibration-certificates",
    CalibrationCertificateViewSet,
    basename="calibration-certificate",
)

app_name = "assets"

urlpatterns = [
    path("", include(router.urls)),
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
]
