from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ================================
# API Documentation Schema
# ================================
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

# ================================
# URL Patterns
# ================================
urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API Endpoints (DRF Browsable API root lives here)
    path("api/v1/", include("api.urls")),

    # API Documentation
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api-docs"),  # shortcut
]

# ================================
# Serve Static/Media Files in Development
# ================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")

    try:
        import debug_toolbar
        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
