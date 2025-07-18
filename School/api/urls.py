from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentsViewSet, parent_login, reset_parent_password

# Set up router and register the viewset
router = DefaultRouter()
router.register(r'parents', ParentsViewSet, basename='parents')

# Include both router and custom routes
urlpatterns = [
    path('', include(router.urls)),
    path('parents/login/', parent_login, name='parent-login'),
    path('parents/reset-password/', reset_parent_password, name='reset-parent-password'),
]
