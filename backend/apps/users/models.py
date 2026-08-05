from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
    ADMIN = 'ADMIN', 'Admin'
    TEACHER = 'TEACHER', 'Teacher'
    STUDENT = 'STUDENT', 'Student'
    PARENT = 'PARENT', 'Parent'
    MODERATOR = 'MODERATOR', 'Moderator'
    PARTNER = 'PARTNER', 'Partner'


class UserStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Actif'
    SUSPENDED = 'SUSPENDED', 'Suspendu'
    DELETED = 'DELETED', 'Supprimé'


class Role(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Code métier du rôle")
    name = models.CharField(max_length=100, help_text="Nom affiché du rôle")
    description = models.TextField(blank=True, default='')
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True, help_text="Code de permission, ex: users.read")
    module = models.CharField(max_length=50, default='general', help_text="Module associé")
    name = models.CharField(max_length=120, help_text="Nom lisible de la permission")
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['module', 'code']

    def __str__(self):
        return self.code


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.name} -> {self.permission.code}"


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name="Téléphone")
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Photo de profil")
    bio = models.TextField(blank=True, default='', verbose_name="Biographie")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        help_text="Rôle principal de l'utilisateur dans le système"
    )

    def save(self, *args, **kwargs):
        if self.role:
            self.role = str(self.role).upper()
        return super().save(*args, **kwargs)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        help_text="Statut du compte"
    )
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Supprimé le")
    children = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='parents', help_text="Enfants de cet utilisateur (pour le rôle de Parent)")
    roles = models.ManyToManyField(Role, blank=True, related_name='users', help_text="Rôles RBAC supplémentaires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def normalized_role(self):
        return str(self.role or '').upper()

    @property
    def is_deleted(self):
        return self.status == UserStatus.DELETED or self.deleted_at is not None

    @property
    def is_super_admin(self):
        return self.normalized_role == UserRole.SUPER_ADMIN or self.is_superuser

    @property
    def is_admin(self):
        return self.normalized_role in [UserRole.ADMIN, UserRole.SUPER_ADMIN] or self.is_superuser

    @property
    def is_teacher(self):
        return self.normalized_role == UserRole.TEACHER

    @property
    def is_student(self):
        return self.normalized_role == UserRole.STUDENT

    @property
    def is_parent(self):
        return self.normalized_role == UserRole.PARENT

    @property
    def is_moderator(self):
        return self.normalized_role == UserRole.MODERATOR

    @property
    def is_partner(self):
        return self.normalized_role == UserRole.PARTNER

    def has_role(self, role_code):
        if self.normalized_role == str(role_code).upper():
            return True
        return self.roles.filter(code=role_code).exists()

    def has_permission(self, permission_code):
        if self.is_superuser or self.is_super_admin:
            return True
        return RolePermission.objects.filter(
            role__in=self.roles.all(),
            permission__code=permission_code
        ).exists()

    def soft_delete(self):
        self.status = UserStatus.DELETED
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['status', 'deleted_at', 'is_active', 'updated_at'])

    def __str__(self):
        return f"{self.username} [{self.get_role_display()}]"
