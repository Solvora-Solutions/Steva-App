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
router.register(r'users', UserViewSet, basename='users')
router.register(r'parents', ParentViewSet, basename='parents')
router.register(r'students', StudentViewSet, basename='students')

# ================================
# URL Patterns
# ================================
urlpatterns = [
    # ============================
    # CRUD endpoints (ViewSets)
    # ============================
    path('', include(router.urls)),

    # ============================
    # Authentication endpoints
    # ============================
    path('auth/login/', unified_login, name='unified_login'),
    path('auth/logout/', user_logout, name='user_logout'),
    path('auth/profile/', user_profile, name='user_profile'),
    path('auth/change-password/', change_password, name='change_password'),
    
    # ============================
    # Password Reset endpoints
    # ============================
    path('auth/password-reset/', request_password_reset, name='request_password_reset'),
    path('auth/password-reset-confirm/<str:uid>/<str:token>/', confirm_password_reset, name='confirm_password_reset'),
    
    # ============================
    # JWT Token endpoints (alternative)
    # ============================
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# ================================
# URL patterns with descriptions
# ================================
"""
API Endpoints Documentation:

CRUD Operations:
- GET    /api/users/           - List users (admin only)
- POST   /api/users/           - Create user (registration)
- GET    /api/users/{id}/      - Get specific user
- PUT    /api/users/{id}/      - Update user
- PATCH  /api/users/{id}/      - Partial update user
- DELETE /api/users/{id}/      - Delete user

- GET    /api/parents/         - List parents (admin only)
- POST   /api/parents/         - Create parent
- GET    /api/parents/{id}/    - Get specific parent
- PUT    /api/parents/{id}/    - Update parent
- PATCH  /api/parents/{id}/    - Partial update parent
- DELETE /api/parents/{id}/    - Delete parent

- GET    /api/students/        - List students (admin only)
- POST   /api/students/        - Create student
- GET    /api/students/{id}/   - Get specific student
- PUT    /api/students/{id}/   - Update student
- PATCH  /api/students/{id}/   - Partial update student
- DELETE /api/students/{id}/   - Delete student

Authentication:
- POST   /api/auth/login/                           - Login (all roles)
- POST   /api/auth/logout/                          - Logout
- GET    /api/auth/profile/                         - Get current user profile
- POST   /api/auth/change-password/                 - Change password (authenticated)

Password Reset:
- POST   /api/auth/password-reset/                  - Request password reset
- POST   /api/auth/password-reset-confirm/<uid>/<token>/  - Confirm password reset

JWT Tokens (alternative):
- POST   /api/auth/token/                           - Get JWT tokens
- POST   /api/auth/token/refresh/                   - Refresh JWT token



"""