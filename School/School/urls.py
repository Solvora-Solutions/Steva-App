from django.contrib import admin
from django.urls import path, include, re_path
<<<<<<< Updated upstream
=======
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.urls import path, re_path, include
>>>>>>> Stashed changes
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

<<<<<<< Updated upstream
=======
# ================================
# API Documentation Schema
# ================================
# JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

>>>>>>> Stashed changes
# Swagger schema
schema_view = get_schema_view(
    openapi.Info(
        title="Steva School API",
        default_version='v1',
        description="API documentation for Steva School App",
        contact=openapi.Contact(email="stevaacademy994@gmail.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API (all endpoints handled in api/urls.py)
    path('api/v1/', include('api.urls')),

<<<<<<< Updated upstream
=======
    # API Documentation
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("docs/", RedirectView.as_view(url="/swagger/", permanent=False), name="api-docs-redirect"),

    # Root redirect
    path("", RedirectView.as_view(url="/swagger/", permanent=False)),
    # Payments app
    path('api/v1/payments/', include('payments.urls')),

    # ✅ JWT Authentication endpoints
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

>>>>>>> Stashed changes
    # Swagger/OpenAPI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
