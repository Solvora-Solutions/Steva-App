from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError

from Parent.models import Parent
from Student.models import Student
from .serializers import UserSerializer, ParentSerializer, StudentSerializer

User = get_user_model()


# =========================
# USER VIEWSET
# =========================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if getattr(self, 'swagger_fake_view', False):
            return [AllowAny()]  # Allow schema generation
        if self.action in ['create']:
            return [AllowAny()]
        elif self.action in ['list']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email', '').strip()
            if email:
                validate_email(email)
            return super().create(request, *args, **kwargs)
        except ValidationError:
            return Response({"detail": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"detail": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# PARENT VIEWSET
# =========================
class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.select_related('user').all()
    serializer_class = ParentSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if getattr(self, 'swagger_fake_view', False):
            return [AllowAny()]
        if self.action in ['create']:
            return [AllowAny()]
        elif self.action in ['list']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Parent.objects.none()
        if self.request.user.is_staff:
            return Parent.objects.select_related('user').all()
        return Parent.objects.select_related('user').filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "Parent creation failed: duplicate email or data."},
                status=status.HTTP_400_BAD_REQUEST
            )


# =========================
# STUDENT VIEWSET
# =========================
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if getattr(self, 'swagger_fake_view', False):
            return [AllowAny()]
        if self.action in ['list']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Student.objects.none()
        if self.request.user.is_staff:
            return Student.objects.all()
        parent_qs = Parent.objects.filter(user=self.request.user)
        if parent_qs.exists():
            return Student.objects.filter(parent=parent_qs.first())
        return Student.objects.none()


# =========================
# UNIFIED LOGIN
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def unified_login(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_email(email)
    except ValidationError:
        return Response({'detail': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return Response({'detail': 'Account is disabled.'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    user_role = 'admin' if user.is_staff else 'parent'

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user_role,
            'is_staff': user.is_staff,
        }
    }, status=status.HTTP_200_OK)


# =========================
# LOGOUT
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# PASSWORD RESET REQUEST
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email', '').strip()
    if not email:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_email(email)
    except ValidationError:
        return Response({'detail': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        if user.is_active:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            subject = "Password Reset Request"
            message = f"""
Hi {user.first_name},

You requested a password reset. Click the link below to reset your password:
{reset_link}

If you didn't request this, please ignore this email.
"""
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        return Response({'detail': 'If an account with this email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'If an account with this email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)


# =========================
# PASSWORD RESET CONFIRM
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request, uid, token):
    new_password = request.data.get('new_password', '')
    confirm_password = request.data.get('confirm_password', '')
    if not new_password or not confirm_password:
        return Response({'detail': 'New password and confirmation are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if new_password != confirm_password:
        return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new_password) < 8:
        return Response({'detail': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            RefreshToken.for_user(user)
            return Response({'detail': 'Password reset successful. Please login with your new password.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid or expired reset link.'}, status=status.HTTP_400_BAD_REQUEST)
    except (User.DoesNotExist, ValueError, OverflowError):
        return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# CHANGE PASSWORD
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get('current_password', '')
    new_password = request.data.get('new_password', '')
    confirm_password = request.data.get('confirm_password', '')
    if not all([current_password, new_password, confirm_password]):
        return Response({'detail': 'All password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if new_password != confirm_password:
        return Response({'detail': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new_password) < 8:
        return Response({'detail': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    if not user.check_password(current_password):
        return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)


# =========================
# GET USER PROFILE
# =========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    user_data = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': 'admin' if user.is_staff else 'parent',
        'is_staff': user.is_staff,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }

    parent_qs = Parent.objects.filter(user=user)
    if parent_qs.exists():
        parent = parent_qs.first()
        user_data['parent_info'] = {
            'phone_number': getattr(parent, 'phone_number', ''),
            'address': getattr(parent, 'address', ''),
        }

    return Response(user_data, status=status.HTTP_200_OK)
