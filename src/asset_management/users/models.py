from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("manager", "Department Manager"),
        ("technician", "Technician"),
        ("researcher", "Researcher"),
        ("auditor", "Auditor"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="researcher")
    department = models.ForeignKey(
        "assets.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    phone = models.CharField(max_length=20, blank=True)
    office_location = models.ForeignKey(
        "assets.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="occupants",
    )
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_manager(self):
        return self.role == "manager"

    @property
    def is_technician(self):
        return self.role == "technician"

    @property
    def is_auditor(self):
        return self.role == "auditor"
