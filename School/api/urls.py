from django.urls import path, include
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('healthz/', views.health_check, name='health-check'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.unified_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('oauth-urls/', views.oauth_urls, name='oauth-urls'),
    path('password-reset/', views.request_password_reset, name='password-reset'),
    path('password-reset/<uidb64>/<token>/', views.confirm_password_reset, name='confirm-password-reset'),
    path('change-password/', views.change_password, name='change-password'),
    path('profile/', views.user_profile, name='profile'),
    path('users/', views.UserViewSet.as_view({'get': 'list'}), name='users'),
    path('parents/', views.ParentViewSet.as_view({'get': 'list'}), name='parents'),
    path('students/', views.StudentViewSet.as_view({'get': 'list', 'post': 'create'}), name='students'),
    path('students/<int:pk>/', views.StudentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='student-detail'),
    # Auth endpoints for frontend compatibility
    path('auth/', include([
        path('login/', views.unified_login, name='auth-login'),
        path('register/', views.RegisterView.as_view(), name='auth-register'),
        path('logout/', views.user_logout, name='auth-logout'),
        path('profile/', views.user_profile, name='auth-profile'),
    ])),
]
