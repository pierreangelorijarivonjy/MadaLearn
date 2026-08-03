from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    TEACHER = 'TEACHER', 'Teacher'
    STUDENT = 'STUDENT', 'Student'


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        help_text="Rôle de l'utilisateur dans le système (ADMIN, TEACHER, STUDENT)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == UserRole.TEACHER

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT

    def __str__(self):
        return f"{self.username} [{self.role}]"
