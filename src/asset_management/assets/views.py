from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Location,
    Department,
    Instrument,
    Review,
    MaintenanceRecord,
    CalibrationRecord,
    CalibrationCertificate,
    Site,
)
from .serializers import (
    LocationSerializer,
    DepartmentSerializer,
    InstrumentSerializer,
    ReviewSerializer,
    MaintenanceRecordSerializer,
    CalibrationRecordSerializer,
    CalibrationCertificateSerializer,
    SiteSerializer,
)
from django.db import models
from rest_framework.decorators import action
from rest_framework.response import Response
from asset_management.api.permissions import (
    IsAdminOrManager,
    IsTechnician,
    IsAuditor,
)
from django.utils import timezone
from .services import TicketService

# Create your views here.


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["building", "room"]
    search_fields = ["name", "building", "room"]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["code"]
    search_fields = ["name", "code"]


class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "review_status", "department", "location"]
    search_fields = ["name", "serial_number", "model", "manufacturer"]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "status",
        "priority",
        "instrument",
        "requested_by",
        "assigned_to",
    ]
    search_fields = ["reason"]

    def get_queryset(self):
        queryset = Review.objects.all()
        if not self.request.user.is_staff:
            # Non-staff users can only see reviews they requested or are assigned to
            queryset = queryset.filter(
                models.Q(requested_by=self.request.user)
                | models.Q(assigned_to=self.request.user)
                | models.Q(instrument__department=self.request.user.department)
            )
        return queryset

    def get_permissions(self):
        """
        Add IsAdminUser permission for update and delete operations.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def create_ticket(self, request, pk=None):
        """Create a ticket for the review in the external system."""
        review = self.get_object()
        ticket_service = TicketService()
        ticket_data = ticket_service.create_ticket(review)

        if not ticket_data:
            return Response(
                {"detail": "Failed to create ticket in external system"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        review.external_ticket_id = ticket_data["ticket_id"]
        review.external_ticket_url = ticket_data["ticket_url"]
        review.save()

        return Response(ticket_data, status=status.HTTP_201_CREATED)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "maintenance_type", "instrument"]
    search_fields = ["description"]


class CalibrationRecordViewSet(viewsets.ModelViewSet):
    queryset = CalibrationRecord.objects.all()
    serializer_class = CalibrationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "calibration_type", "instrument"]
    search_fields = ["description"]


class CalibrationCertificateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing calibration certificates.
    """

    queryset = CalibrationCertificate.objects.all()
    serializer_class = CalibrationCertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Add IsAdminUser permission for create, update, and delete operations.
        """
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "create_version",
            "review",
        ]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filter certificates based on user permissions.
        """
        queryset = CalibrationCertificate.objects.all()
        if not self.request.user.is_staff:
            # Regular users can only see approved certificates
            queryset = queryset.filter(is_approved=True)
        return queryset

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """
        Add a QA review to a certificate.
        """
        certificate = self.get_object()
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can review certificates"},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_approved = request.data.get("is_approved", False)
        review_notes = request.data.get("review_notes", "")

        certificate.reviewer = request.user
        certificate.review_date = timezone.now()
        certificate.review_notes = review_notes
        certificate.is_approved = is_approved
        certificate.status = (
            CalibrationCertificate.APPROVED
            if is_approved
            else CalibrationCertificate.REJECTED
        )
        certificate.save()

        return Response(self.get_serializer(certificate).data)

    @action(detail=True, methods=["post"])
    def create_version(self, request, pk=None):
        """
        Create a new version of a certificate.
        """
        certificate = self.get_object()
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can create new versions"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create new version
        new_certificate = CalibrationCertificate.objects.create(
            certificate_number=certificate.certificate_number,
            version=certificate.version + 1,
            status=CalibrationCertificate.DRAFT,
            issue_date=timezone.now().date(),
            expiry_date=certificate.expiry_date,
            certificate_type=certificate.certificate_type,
            created_by=request.user,
            calibration_data=certificate.calibration_data,
        )

        # Mark old version as superseded
        certificate.status = CalibrationCertificate.SUPERSEDED
        certificate.save()

        return Response(
            self.get_serializer(new_certificate).data, status=status.HTTP_201_CREATED
        )


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["code", "is_active"]
    search_fields = ["name", "code", "address"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
