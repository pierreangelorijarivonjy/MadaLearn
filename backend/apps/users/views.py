from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer
)
from core.permissions import IsAdminUser


class RegisterView(generics.CreateAPIView):
    """
    Endpoint d'inscription pour les utilisateurs (ADMIN, TEACHER, STUDENT).
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Endpoint de consultation et modification du profil de l'utilisateur connecté.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint de connexion JWT renvoyant les jetons Access, Refresh et le profil utilisateur.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserListView(generics.ListAPIView):
    """
    Endpoint d'administration pour lister les utilisateurs (Réservé aux Admin).
    """
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
