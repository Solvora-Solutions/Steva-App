from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    ParentViewSet,
    StudentViewSet,
    unified_login,
    user_logout,
    reset_password
)

# ================================
# Router setup
# ================================
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'parents', ParentViewSet, basename='parents')
router.register(r'students', StudentViewSet, basename='students')

# ================================
# URL Patterns
# ================================
urlpatterns = [
    # CRUD endpoints
    path('', include(router.urls)),

    # Authentication (unified for all roles)
    path('auth/login/', unified_login, name='login'),
    path('auth/logout/', user_logout, name='logout'),
    path('auth/reset-password/', reset_password, name='reset-password'),

    # JWT token endpoints (optional)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
