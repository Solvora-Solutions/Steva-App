from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.utils.encoding import force_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.db import transaction

from rest_framework import status, viewsets, generics, permissions, throttling
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import re

from Parent.models import Parent 
from Student.models import Student
from .serializers import (
    UserSerializer,
    ParentSerializer,
    StudentSerializer,
    RegisterSerializer,
)
from .utils import send_safe_mail


User = get_user_model()


# ============================
# Helpers
# ============================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_email_format(email: str) -> bool:
    """
    Validate email format using Django's validator and a more comprehensive regex.
    """
    if not email or len(email) > 254:  # RFC 5321 limit
        return False
    try:
        validate_email(email)
        # More comprehensive regex that handles international domains and special characters
        return re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email) is not None
    except DjangoValidationError:
        return False


def blacklist_all_user_refresh_tokens(user):
    """
    Blacklist all outstanding refresh tokens for the given user.
    Safe to call multiple times.
    """
    for outstanding in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding)


# ============================
# Throttling
# ============================
class BurstRateThrottle(throttling.UserRateThrottle):
    rate = "3/min"


class SustainedRateThrottle(throttling.UserRateThrottle):
    rate = "50/day"


class AuthRateThrottle(throttling.UserRateThrottle):
    rate = "5/min"


class PasswordResetThrottle(throttling.UserRateThrottle):
    rate = "2/min"


# ============================
# Registration
# ============================
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle, SustainedRateThrottle]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "").strip()

        if not email:
            return Response({"success": False, "message": "Email is required"}, status=400)
        if not password:
            return Response({"success": False, "message": "Password is required"}, status=400)
        if not validate_email_format(email):
            return Response({"success": False, "message": "Invalid email format"}, status=400)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            # Create related profile if applicable
            if getattr(user, "is_parent", False):
                Parent.objects.get_or_create(user=user)
            if getattr(user, "is_student", False):
                Student.objects.get_or_create(user=user)

            return Response(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "user": UserSerializer(user).data,
                    "tokens": tokens,
                },
                status=201,
            )

        return Response(
            {"success": False, "message": "Invalid data", "errors": serializer.errors},
            status=400,
        )


# ============================
# Unified Login (email, Google, Facebook, Apple)
# ============================
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([AuthRateThrottle, SustainedRateThrottle])
def unified_login(request):
    login_type = request.data.get("type")

    if not login_type:
        return Response({"success": False, "message": "Login type is required"}, status=400)

    try:
        # ----- Google Login -----
        if login_type == "google":
            token = request.data.get("token")
            if not token:
                return Response({"success": False, "message": "Google token is required"}, status=400)

            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            email = normalize_email(idinfo["email"])

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": idinfo.get("given_name", ""),
                    "last_name": idinfo.get("family_name", ""),
                }
            )

            # Log Google login for security monitoring
            import logging
            logger = logging.getLogger(__name__)
            if created:
                logger.info(f"New user created via Google login: {user.email}")
            else:
                logger.info(f"Existing user logged in via Google: {user.email}")

            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "success": True,
                    "message": "Google login successful",
                    "user": UserSerializer(user).data,
                    "tokens": tokens,
                }
            )

        # ----- Email/Password Login -----
        elif login_type == "email":
            email = request.data.get("email", "").strip()
            password = request.data.get("password", "").strip()

            if not email:
                return Response({"success": False, "message": "Email is required"}, status=400)
            if not password:
                return Response({"success": False, "message": "Password is required"}, status=400)
            if not validate_email_format(email):
                return Response({"success": False, "message": "Invalid email format"}, status=400)

            email = normalize_email(email)

            # Prevent user enumeration via timing
            user = None
            user_exists = False
            try:
                candidate = User.objects.get(email=email)
                user_exists = True

                # Check if account is locked
                if candidate.is_locked():
                    return Response({"success": False, "message": "Account is temporarily locked due to too many failed login attempts. Please try again later."}, status=429)

                if candidate.check_password(password):
                    user = candidate
                    # Reset failed attempts on successful login
                    user.reset_failed_attempts()
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                else:
                    # Increment failed attempts on wrong password
                    candidate.increment_failed_attempts()
            except User.DoesNotExist:
                pass
            if not user_exists:
                # perform dummy hash to keep timing similar
                User().set_password(password)

            if user is None:
                return Response({"success": False, "message": "Invalid credentials"}, status=401)

            tokens = get_tokens_for_user(user)
            return Response(
                {"success": True, "message": "Login successful", "user": UserSerializer(user).data, "tokens": tokens}
            )

        return Response(
            {"success": False, "message": "Invalid login type. Use 'email', 'google', 'facebook', or 'apple'"},
            status=400,
        )

    except ValueError:
        # Log the error for debugging but don't expose details to user
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Invalid Google OAuth token provided")
        return Response({"success": False, "message": "Invalid authentication token"}, status=400)
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Login failed: {str(e)}")
        return Response({"success": False, "message": "Login failed. Please try again later."}, status=500)


# ============================
# OAuth URLs for Frontend
# ============================
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def oauth_urls(request):
    """Return OAuth login URLs for frontend redirection."""
    from django.urls import reverse
    from django.contrib.sites.models import Site

    try:
        current_site = Site.objects.get_current()
        base_url = f"https://{current_site.domain}" if not settings.DEBUG else "http://127.0.0.1:8000"
    except:
        base_url = "http://127.0.0.1:8000" if settings.DEBUG else "https://yourdomain.com"

    urls = {
        "google": f"{base_url}/auth/login/google-oauth2/",
        "facebook": f"{base_url}/auth/login/facebook/",
        "apple": f"{base_url}/auth/login/apple-id/",
    }

    return Response({
        "success": True,
        "oauth_urls": urls,
        "message": "Use these URLs to redirect users to OAuth providers"
    })


# ============================
# Logout (blacklist provided refresh token)
# ============================
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def user_logout(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"success": False, "message": "Refresh token required"}, status=400)
    try:
        RefreshToken(refresh_token).blacklist()
        return Response({"success": True, "message": "Logged out successfully"})
    except TokenError:
        return Response({"success": False, "message": "Invalid or expired token"}, status=400)
    except Exception:
        return Response({"success": False, "message": "Logout failed"}, status=500)


# ============================
# Password Reset
# ============================
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([PasswordResetThrottle, SustainedRateThrottle])
def request_password_reset(request):
    email = request.data.get("email", "").strip()
    if not email:
        return Response({"success": False, "message": "Email is required"}, status=400)
    if not validate_email_format(email):
        return Response({"success": False, "message": "Invalid email format"}, status=400)

    email = normalize_email(email)
    user = User.objects.filter(email=email).first()

    # Always return the same response to prevent user enumeration
    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        # Ensure FRONTEND_URL is configured
        frontend_url = getattr(settings, 'FRONTEND_URL', None)
        if not frontend_url:
            # Log error and return generic response
            import logging
            logger = logging.getLogger(__name__)
            logger.error("FRONTEND_URL not configured in settings")
            return Response({"success": True, "message": "If this email exists, a reset link has been sent."})

        reset_link = f"{frontend_url.rstrip('/')}/reset-password/{uid}/{token}/"
        send_safe_mail(
            "Password Reset Request",
            f"""You requested a password reset for your account.

Use this link to reset your password: {reset_link}

This link will expire in 24 hours.

If you didn't request this reset, please ignore this email.
Your password will remain unchanged.""",
            [user.email],
        )

        # Log password reset attempt for security monitoring
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Password reset email sent to user: {user.email}")

    # Generic response to avoid enumeration
    return Response({"success": True, "message": "If this email exists, a reset link has been sent."})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def confirm_password_reset(request, uid, token):
    password = request.data.get("password", "").strip()
    if not password:
        return Response({"success": False, "message": "Password is required"}, status=400)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (DjangoUnicodeDecodeError, User.DoesNotExist):
        return Response({"success": False, "message": "Invalid reset link"}, status=400)

    if not default_token_generator.check_token(user, token):
        # Log failed password reset attempt
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Invalid or expired password reset token for user: {user.email}")
        return Response({"success": False, "message": "Invalid or expired token"}, status=400)

    try:
        validate_password(password, user)
    except DjangoValidationError as e:
        return Response(
            {"success": False, "message": "Password validation failed", "errors": e.messages},
            status=400,
        )

    user.set_password(password)
    user.save()

    # 🔒 Invalidate all existing refresh tokens
    blacklist_all_user_refresh_tokens(user)

    # Log successful password reset
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Password successfully reset for user: {user.email}")

    return Response({"success": True, "message": "Password reset successful. Please log in again."})


# ============================
# Change Password
# ============================
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def change_password(request):
    user = request.user
    old_password = request.data.get("old_password", "").strip()
    new_password = request.data.get("new_password", "").strip()

    if not old_password:
        return Response({"success": False, "message": "Old password is required"}, status=400)
    if not new_password:
        return Response({"success": False, "message": "New password is required"}, status=400)
    if not user.check_password(old_password):
        return Response({"success": False, "message": "Old password is incorrect"}, status=400)

    try:
        validate_password(new_password, user)
    except DjangoValidationError as e:
        return Response(
            {"success": False, "message": "Password validation failed", "errors": e.messages},
            status=400,
        )

    user.set_password(new_password)
    user.save()

    # 🔒 Invalidate all existing refresh tokens
    blacklist_all_user_refresh_tokens(user)

    return Response({"success": True, "message": "Password changed successfully. Please log in again."})


# ============================
# User Profile
# ============================
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    return Response({"success": True, "user": UserSerializer(request.user).data})


# ============================
# ViewSets
# ============================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ParentViewSet(viewsets.ModelViewSet):
    serializer_class = ParentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Parent.objects.filter(user=self.request.user)


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return students where the logged-in user is one of the parents
        return Student.objects.filter(parents=self.request.user)
