from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationViewSet,
    DepartmentViewSet,
    InstrumentViewSet,
    MaintenanceRecordViewSet,
    CalibrationRecordViewSet,
    UserViewSet,
    HealthCheckViewSet,
    ReviewViewSet,
)
from asset_management.assets.views import CalibrationCertificateViewSet, SiteViewSet

router = DefaultRouter()
router.register(r"locations", LocationViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"instruments", InstrumentViewSet)
router.register(r"maintenance", MaintenanceRecordViewSet)
router.register(r"calibration-records", CalibrationRecordViewSet)
router.register(r"users", UserViewSet)
router.register(r"health", HealthCheckViewSet, basename="health")
router.register(r"reviews", ReviewViewSet)
router.register(r"calibration-certificates", CalibrationCertificateViewSet)
router.register(r"sites", SiteViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
