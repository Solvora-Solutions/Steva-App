from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    ParentViewSet,
    StudentViewSet,
    RegisterView,
    unified_login,
    user_logout,
    request_password_reset,
    confirm_password_reset,
    change_password,
    user_profile,
)

app_name = "api"

# Use DRF Router for ViewSets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"parents", ParentViewSet, basename="parent")
router.register(r"students", StudentViewSet, basename="student")

urlpatterns = [
    # Router endpoints for CRUD
    path("", include(router.urls)),

    # Registration
    path("auth/register/", RegisterView.as_view(), name="register"),

    # Custom Auth endpoints
    path("auth/login/", unified_login, name="unified_login"),   # Supports email/phone login
    path("auth/logout/", user_logout, name="user_logout"),
    path("auth/profile/", user_profile, name="user_profile"),
    path("auth/change-password/", change_password, name="change_password"),

    # Password Reset Flow
    path("auth/password-reset/", request_password_reset, name="request_password_reset"),
    path(
        "auth/password-reset-confirm/<str:uid>/<str:token>/",
        confirm_password_reset,
        name="confirm_password_reset",
    ),

    # JWT Token endpoints
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
