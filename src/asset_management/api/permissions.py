from rest_framework import permissions


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_staff or request.user.role == "manager"

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        if request.user.role == "manager":
            # Managers can only modify objects in their department
            if hasattr(obj, "department"):
                return obj.department == request.user.department
            return False
        return False


class IsTechnician(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == "technician"

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "technician":
            # Technicians can only modify maintenance and calibration records
            if hasattr(obj, "instrument"):
                return obj.instrument.department == request.user.department
            return False
        return False


class IsAuditor(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == "auditor"

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "auditor":
            # Auditors have read-only access to all objects
            return request.method in permissions.SAFE_METHODS
        return False


class IsResearcher(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == "researcher"

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "researcher":
            # Researchers can only view instruments and request them
            if hasattr(obj, "department"):
                return request.method in permissions.SAFE_METHODS
            return False
        return False
