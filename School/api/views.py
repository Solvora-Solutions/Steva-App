from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from .serializers import ParentSerializer
from Parent.models import Parent


# ========== PARENT VIEWSET ==========
class ParentsViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Parent model.
    Accessible only to authenticated users.
    """
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        parent = serializer.save()
        user = parent.user
        password = self.request.data.get("user", {}).get("password")
        if password:
            user.set_password(password)
            user.save()


# ========== PARENT LOGIN ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def parent_login(request):
    """
    Log in a parent using email and password.

    Returns:
        JWT access and refresh tokens if authentication is successful.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'detail': 'Email and password are required.'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=email, password=password)

    if user and hasattr(user, 'parent'):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

    return Response({'detail': 'Invalid credentials or not a parent.'},
                    status=status.HTTP_401_UNAUTHORIZED)


# ========== PARENT PASSWORD RESET ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_parent_password(request):
    """
    Reset a parent's password using their email and new password.
    """
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({'detail': 'Email and new password are required.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        parent = Parent.objects.select_related('user').get(user__email=email)
        user = parent.user
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password reset successful.'},
                        status=status.HTTP_200_OK)

    except Parent.DoesNotExist:
        return Response({'detail': 'No parent found with this email.'},
                        status=status.HTTP_404_NOT_FOUND)
