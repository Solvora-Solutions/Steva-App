# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    ParentViewSet,
    StudentViewSet,
    unified_login,
    user_logout,
    request_password_reset,
    confirm_password_reset,
    change_password,
    user_profile,
)

# ================================
# Router setup for ViewSets
# ================================
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"parents", ParentViewSet, basename="parent")
router.register(r"students", StudentViewSet, basename="student")

# ================================
# URL Patterns
# ================================
urlpatterns = [
    # API Root & ViewSets (Browsable API root available at /api/v1/)
    path("", include(router.urls)),

    # Custom Auth Endpoints
    path("auth/login/", unified_login, name="unified_login"),
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

    # JWT Endpoints (optional, if you want token-based login instead of unified_login)
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
