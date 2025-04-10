from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ..assets.models import Location, Department, Instrument
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your tests here.
