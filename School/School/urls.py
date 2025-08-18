from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ================================
# API Documentation Schema
# ================================
schema_view = get_schema_view(
    openapi.Info(
        title="Steva School API",
        default_version='v1',
        description="API documentation for Steva School App",
        contact=openapi.Contact(email="eetpanford@st.ug.edu.gh"),
    ),
    public=True,
    permission_classes=[permissions.IsAdminUser],
)

# ================================
# URL Patterns
# ================================
urlpatterns = [
    # ============================
    # Admin Interface
    # ============================
    path('admin/', admin.site.urls),

    # ============================
    # API Endpoints
    # ============================
    path('api/v1/', include('api.urls')),
    path('api/', RedirectView.as_view(url='/api/v1/', permanent=True)),  # Permanent is fine for versioning

    # ============================
    # API Documentation
    # ============================
    # JSON/YAML schema endpoints
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    
    # Interactive documentation
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    path(
        'docs/',
        RedirectView.as_view(url='/swagger/', permanent=False),  # Changed to temporary redirect
        name='api-docs-redirect'
    ),

    # ============================
    # Root redirect
    # ============================
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),  # Changed to temporary redirect
]

# ================================
# Serve Static/Media Files in Development
# ================================
if settings.DEBUG:
    # Serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar if installed
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# ================================
# Admin Site Customization
# ================================
admin.site.site_header = "Steva School Administration"
admin.site.site_title = "Steva School Admin"
admin.site.index_title = "Welcome to Steva School Administration Portal"
