from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ============================
# API Documentation (Swagger/Redoc)
# ============================
schema_view = get_schema_view(
    openapi.Info(
        title="Steva School API",
        default_version="v1",
        description="API documentation for Steva School App",
        contact=openapi.Contact(email="eetpanford@st.ug.edu.gh"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# ============================
# URL Patterns
# ============================
urlpatterns = [
    # Admin Dashboard
    path("admin/", admin.site.urls),

    # Core API (versioned)
    path("api/v1/", include("api.urls", namespace="api")),

    # Google OAuth2 (social-auth-app-django)
    # Login   → /auth/login/google-oauth2/
    # Callback → /auth/complete/google-oauth2/
    path("auth/", include("social_django.urls", namespace="social")),

    # API Docs (Swagger & Redoc)
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# ============================
# Media & Static (Dev only)
# ============================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
