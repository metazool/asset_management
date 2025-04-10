from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from .serializers import UserSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """
        Filter queryset to return only active users.
        """
        return self.queryset.filter(is_active=True)
