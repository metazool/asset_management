from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters import rest_framework as filters
from asset_management.assets.models import (
    Location,
    Department,
    Instrument,
    MaintenanceRecord,
    CalibrationRecord,
    Review,
)
from django.contrib.auth import get_user_model
from .serializers import (
    LocationSerializer,
    DepartmentSerializer,
    InstrumentSerializer,
    MaintenanceRecordSerializer,
    CalibrationRecordSerializer,
    UserSerializer,
    ReviewSerializer,
)
from .permissions import (
    IsAdminOrManager,
    IsTechnician,
    IsAuditor,
)
from rest_framework import status
from asset_management.assets.services import TicketService

User = get_user_model()


class HealthCheckViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        return Response({"status": "healthy"})


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated & (IsAdminOrManager | IsAuditor)]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["building", "room"]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated & (IsAdminOrManager | IsAuditor)]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["name", "manager"]


class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["status", "category", "department", "location"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "auditor":
            return Instrument.objects.all()
        elif user.role == "manager":
            return Instrument.objects.filter(department=user.department)
        elif user.role in ["technician", "researcher"]:
            return Instrument.objects.filter(department=user.department)
        return Instrument.objects.none()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["status", "instrument", "date_scheduled"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "auditor":
            return MaintenanceRecord.objects.all()
        elif user.role in ["manager", "technician"]:
            return MaintenanceRecord.objects.filter(
                instrument__department=user.department
            )
        return MaintenanceRecord.objects.none()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAdminOrManager | IsTechnician]
        elif self.action == "destroy":
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class CalibrationRecordViewSet(viewsets.ModelViewSet):
    queryset = CalibrationRecord.objects.all()
    serializer_class = CalibrationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["status", "calibration_type", "instrument", "date_performed"]

    def get_queryset(self):
        user = self.request.user
        queryset = CalibrationRecord.objects.all()

        # Filter by user's role and department for write operations
        if self.action in ["create", "update", "partial_update", "destroy"]:
            if not user.is_staff and user.role != "auditor":
                if user.role in ["manager", "technician"]:
                    queryset = queryset.filter(instrument__department=user.department)
                else:
                    queryset = CalibrationRecord.objects.none()

        # Apply search if provided
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(description__icontains=search)

        return queryset.order_by("-created_at")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAdminOrManager | IsTechnician]
        elif self.action == "destroy":
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["status", "priority", "instrument"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "auditor":
            return Review.objects.all()
        elif user.role == "manager":
            return Review.objects.filter(instrument__department=user.department)
        else:
            # Regular users can see reviews in their department
            return Review.objects.filter(instrument__department=user.department)

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(
        detail=True,
        methods=["post"],
        url_path="create-ticket",
        url_name="create_ticket",
    )
    def create_ticket(self, request, pk=None):
        review = self.get_object()
        ticket_service = TicketService()

        # Create ticket with data from request
        ticket_data = {
            "title": request.data.get("title", f"Review for {review.instrument}"),
            "description": request.data.get("description", review.reason),
            "priority": request.data.get("priority", review.priority),
            "status": request.data.get("status", "open"),
            "assigned_to": request.data.get("assigned_to", review.assigned_to.id),
        }

        ticket = ticket_service.create_ticket(review)
        review.external_ticket_id = ticket["ticket_id"]
        review.external_ticket_url = ticket["ticket_url"]
        review.save()

        return Response(
            {
                "ticket_id": review.external_ticket_id,
                "ticket_url": review.external_ticket_url,
                **ticket_data,
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["GET"])
def health_check(request):
    """
    Health check endpoint to verify API is running.
    """
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)
