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

from .models import Parent, Student
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
    if not email:
        return False
    try:
        validate_email(email)
        return re.match(r"^[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email) is not None
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
    rate = "5/min"


class SustainedRateThrottle(throttling.UserRateThrottle):
    rate = "100/day"


# ============================
# Registration
# ============================
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]

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
# Unified Login (email or Google)
# ============================
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
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

            user, _ = User.objects.get_or_create(email=email, defaults={"username": email})
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
                if candidate.check_password(password):
                    user = candidate
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
            {"success": False, "message": "Invalid login type. Use 'email' or 'google'"},
            status=400,
        )

    except ValueError:
        return Response({"success": False, "message": "Invalid Google token"}, status=400)
    except Exception:
        return Response({"success": False, "message": "Login failed. Try again later."}, status=500)


# ============================
# Logout (blacklist provided refresh token)
# ============================
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
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
@throttle_classes([BurstRateThrottle])
def request_password_reset(request):
    email = request.data.get("email", "").strip()
    if not email:
        return Response({"success": False, "message": "Email is required"}, status=400)
    if not validate_email_format(email):
        return Response({"success": False, "message": "Invalid email format"}, status=400)

    email = normalize_email(email)
    user = User.objects.filter(email=email).first()
    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        send_safe_mail(
            "Password Reset",
            f"Use this link to reset your password: {reset_link}",
            [user.email],
        )

    # generic response to avoid enumeration
    return Response({"success": True, "message": "If this email exists, a reset link has been sent."})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
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

    return Response({"success": True, "message": "Password reset successful. Please log in again."})


# ============================
# Change Password
# ============================
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
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
