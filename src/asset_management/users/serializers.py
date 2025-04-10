from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)
    department = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser._meta.get_field(
            "department"
        ).remote_field.model.objects.all(),
        required=False,
        allow_null=True,
    )
    phone = serializers.CharField(required=False, allow_blank=True)

    def custom_signup(self, request, user):
        user.role = self.validated_data.get("role", "researcher")
        user.department = self.validated_data.get("department", None)
        user.phone = self.validated_data.get("phone", "")
        user.save()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, read_only=True)
    department = serializers.PrimaryKeyRelatedField(read_only=True)
    phone = serializers.CharField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            "role",
            "department",
            "phone",
            "is_approved",
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "department")
        read_only_fields = ("id",)
