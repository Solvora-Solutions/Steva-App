from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError

from Users.models import User
from Parent.models import Parent
from Student.models import Student
from .serializers import (
    UserSerializer,
    ParentSerializer,
    StudentSerializer,
)

User = get_user_model()

# =========================
# USER REGISTRATION
# =========================
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                user.set_password(request.data["password"])  # securely hash password
                user.save()

                # Auto-create Parent profile for non-staff users
                if not user.is_staff:
                    Parent.objects.create(user=user)

                # Issue JWT tokens
                refresh = RefreshToken.for_user(user)

                return Response({
                    "detail": "Registration successful.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                }, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response(
                    {"detail": "A user with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# USER LOGIN (Email or Phone)
# =========================
@api_view(["POST"])
@permission_classes([AllowAny])
def unified_login(request):
    email_or_phone = request.data.get("email") or request.data.get("phone")
    password = request.data.get("password")

    if not email_or_phone or not password:
        return Response(
            {"detail": "Email/Phone and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email_or_phone)
    except User.DoesNotExist:
        return Response(
            {"detail": "Invalid email/phone or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.check_password(password):
        return Response(
            {"detail": "Invalid email/phone or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        "detail": "Login successful.",
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": UserSerializer(user).data,
    })


# =========================
# USER LOGOUT
# =========================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# USER PROFILE
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# =========================
# CHANGE PASSWORD
# =========================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not user.check_password(old_password):
        return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({"detail": "Password updated successfully."})


# =========================
# PASSWORD RESET
# (Stub implementation — expand with email/SMS logic later)
# =========================
@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    return Response({"detail": "Password reset instructions would be sent."})


@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_password_reset(request, uid, token):
    return Response({"detail": "Password has been reset."})


# =========================
# VIEWSETS
# =========================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
