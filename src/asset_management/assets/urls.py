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

urlpatterns = [
    path("", include(router.urls)),
]
