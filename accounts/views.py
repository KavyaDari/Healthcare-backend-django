from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer


@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='Registers a new user account with secure password hashing. Passwords are never returned in responses.'
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]