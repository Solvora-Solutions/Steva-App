from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from .serializers import ParentSerializer
from Parent.models import Parent
from django.contrib.auth import authenticate


# ========== PARENT VIEWSET (uses ModelViewSet for router support) ==========
class ParentsViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        parent = serializer.save()
        user = parent.user
        if 'password' in serializer.validated_data['user']:
            user.set_password(serializer.validated_data['user']['password'])
            user.save()


# ========== PARENT LOGIN ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def parent_login(request):
    """
    Log in a parent using email and password, return JWT tokens.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(username=email, password=password)

    if user is not None and hasattr(user, 'parent'):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

    return Response({'detail': 'Invalid credentials or not a parent'}, status=status.HTTP_401_UNAUTHORIZED)


# ========== PARENT PASSWORD RESET ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_parent_password(request):
    """
    Reset a parent's password using their email and a new password.
    """
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    try:
        parent = Parent.objects.select_related('user').get(user__email=email)
        user = parent.user
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)

    except Parent.DoesNotExist:
        return Response({'detail': 'Parent with this email not found'}, status=status.HTTP_404_NOT_FOUND)
