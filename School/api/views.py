from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError

from Users.models import User
from Parent.models import Parent
from Student.models import Student
from .serializers import UserSerializer, ParentSerializer, StudentSerializer

User = get_user_model()


# =========================
# USER VIEWSET (Protected)
# =========================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


# =========================
# PARENT VIEWSET (Protected)
# =========================
class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.select_related('user').all()
    serializer_class = ParentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Handles duplicate email gracefully."""
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "Parent creation failed: duplicate email."},
                status=status.HTTP_400_BAD_REQUEST
            )


# =========================
# STUDENT VIEWSET (Protected)
# =========================
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


# =========================
# UNIFIED LOGIN (Public)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def unified_login(request):
    """Unified login for Parents and Admins."""
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'detail': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=email, password=password)
    if not user:
        return Response(
            {'detail': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': getattr(user, 'role', 'parent'),  # default if role not defined
        }
    })


# =========================
# LOGOUT (Protected)
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response(
            {"detail": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response(
            {"detail": "Invalid refresh token."},
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================
# PASSWORD RESET (Public)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response(
            {'detail': 'Email and new password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        parent = Parent.objects.select_related('user').get(user__email=email)
        user = parent.user
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password reset successful.'})
    except Parent.DoesNotExist:
        return Response(
            {'detail': 'No parent found with this email.'},
            status=status.HTTP_404_NOT_FOUND
        )
