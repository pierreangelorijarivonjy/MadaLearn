from rest_framework import generics, permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User, UserRole, UserStatus, Role, Permission, RolePermission
from users.serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    UserAdminSerializer,
    RoleSerializer,
    PermissionSerializer,
    ChangePasswordSerializer,
    AvatarUploadSerializer
)
from core.permissions import IsAdminUser
from activity.models import ActivityLog


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
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        old_role = self.request.user.role
        updated_user = serializer.save()
        if old_role != updated_user.role:
            ActivityLog.objects.create(
                user=updated_user,
                action='role_change',
                module='users',
                description=f"Changement de rôle de {old_role} vers {updated_user.role}",
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint de connexion JWT renvoyant les jetons Access, Refresh et le profil utilisateur.
    """
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(generics.GenericAPIView):
    """
    Endpoint pour changer le mot de passe de l'utilisateur connecté.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"detail": "Ancien mot de passe incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Mot de passe changé avec succès."}, status=status.HTTP_200_OK)


class AvatarUploadView(generics.GenericAPIView):
    """
    Endpoint de gestion de l'avatar (Photo de profil) pour l'utilisateur connecté.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = AvatarUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if user.profile_photo:
            user.profile_photo.delete(save=False)
            
        user.profile_photo = serializer.validated_data['avatar']
        user.save()
        
        # On va re-sérialiser pour renvoyer l'URL
        profile_serializer = UserProfileSerializer(user, context={'request': request})
        return Response(profile_serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.profile_photo:
            user.profile_photo.delete(save=False)
            user.profile_photo = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('role_permissions__permission').all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all().order_by('module', 'code')
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    Endpoint d'administration de gestion complète des utilisateurs (CRUD).
    """
    queryset = User.objects.exclude(status=UserStatus.DELETED).order_by('-created_at')
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = User.objects.exclude(status=UserStatus.DELETED).order_by('-created_at')
        user = self.request.user

        if not user.is_super_admin:
            qs = qs.exclude(role__in=[UserRole.SUPER_ADMIN, UserRole.ADMIN])

        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=str(role).upper())

        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                email__icontains=search
            ) | qs.filter(
                username__icontains=search
            ) | qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            )
        return qs.distinct()

    def perform_create(self, serializer):
        user = self.request.user
        role = serializer.validated_data.get('role')
        if not user.is_super_admin and role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise permissions.PermissionDenied("Seul un Super Admin peut créer un administrateur.")
        created_user = serializer.save()
        ActivityLog.objects.create(
            user=user,
            action='user_create',
            module='users',
            description=f"Création de l'utilisateur {created_user.username}",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        user = self.request.user
        obj = self.get_object()
        role = serializer.validated_data.get('role', obj.role)

        if not user.is_super_admin:
            if obj.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN] or role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
                raise permissions.PermissionDenied("Vous n'avez pas l'autorisation de modifier ce niveau de rôle.")
        updated_user = serializer.save()
        if obj.role != updated_user.role:
            ActivityLog.objects.create(
                user=user,
                action='role_change',
                module='users',
                description=f"Modification du rôle de {obj.username} ({obj.role}) vers {updated_user.role}",
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_super_admin:
            if instance.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
                raise permissions.PermissionDenied("Seul un Super Admin peut supprimer un administrateur.")
        instance.soft_delete()
        ActivityLog.objects.create(
            user=user,
            action='user_delete',
            module='users',
            description=f"Suppression logique de l'utilisateur {instance.username}",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
