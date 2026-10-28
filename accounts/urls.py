from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema
from .views import RegisterView


@extend_schema(
    tags=['Authentication'],
    summary='User login (obtain JWT tokens)',
    description='Authenticate with username and password to obtain JWT access and refresh tokens.'
)
class CustomTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]


@extend_schema(
    tags=['Authentication'],
    summary='Refresh JWT access token',
    description='Provide a valid refresh token to obtain a new JWT access token.'
)
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]