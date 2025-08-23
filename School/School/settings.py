from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-c$+y&hqrsmny4c^nzv(y4&^ic3(_m2pf-+aw1_mz+_85hukqp5'

DEBUG = True

ALLOWED_HOSTS = ["*"]  # Dev: allow all; tighten for production

# ============================
# Application definition
# ============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'Users',
    'Parent',
    'Student',
    'api',
<<<<<<< Updated upstream
=======
    'payments',
>>>>>>> Stashed changes

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # For logout
    'drf_yasg',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Allow frontend requests
    'django.middleware.common.CommonMiddleware',  # Must be after CorsMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'School.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'School.wsgi.application'

# ============================
# Database (SQLite for now)
# ============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================
# Custom User Model
# ============================
AUTH_USER_MODEL = 'Users.User'

# ============================
# Password validation
# ============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================
# REST Framework & JWT Settings
# ============================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Default is IsAuthenticated; views override for login/registration
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ============================
# Swagger JWT Auth
# ============================
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header. Example: "Bearer <your_token>"',
        }
    },
}

# ============================
# CORS Settings (Frontend Access)
# ============================
CORS_ALLOW_ALL_ORIGINS = True  # Dev: Allow all origins
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
    'accept',
    'origin',
    'user-agent',
    'accept-encoding',
    'accept-language',
]

# ============================
# Internationalization
# ============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================
# Static files
# ============================
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================
#Paystack Settings
# ============================
PAYSTACK_SECRET_KEY = 'sk_test_5df109d28a1244ad0cd8003ddd0c1b321a308433'
PAYSTACK_PUBLIC_KEY = 'pk_test_513aeef105294e66d3b0407755b4ae6b6fc87559'

# ============================
# Africa's Talking Settings
# ============================
AFRICASTALKING_USERNAME = 'sandbox'
AFRICASTALKING_API_KEY = 'atsk_b17ffe277702d63f88a46132e9654eba26ab22f4f2173b43c9c5a50bdaea143079423ebd'

#=============================
#Email Settings
#=============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'milleradu776@gmail.com'
EMAIL_HOST_PASSWORD = 'hubc qvhv vfvw bfnw'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER