from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentsViewSet, parent_login, reset_parent_password

# Router setup for ViewSets
router = DefaultRouter()
router.register(r'parents', ParentsViewSet, basename='parents')

# All API routes
urlpatterns = [
    # ViewSet routes (CRUD for parents)
    path('', include(router.urls)),

    # Custom parent authentication routes
    path('parents/login/', parent_login, name='parent-login'),
    path('parents/reset-password/', reset_parent_password, name='reset-parent-password'),
]
