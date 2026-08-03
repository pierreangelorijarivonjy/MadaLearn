from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import UserRole


class IsAdminUser(BasePermission):
    """
    Accès réservé exclusivement aux Administrateurs et Superutilisateurs.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsTeacherUser(BasePermission):
    """
    Accès réservé aux Enseignants et Admins.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == UserRole.TEACHER or request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsStudentUser(BasePermission):
    """
    Accès réservé aux Étudiants.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == UserRole.STUDENT or request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsTeacherOrReadOnly(BasePermission):
    """
    Lecture autorisée à tous les utilisateurs authentifiés.
    Création, modification et suppression réservées aux Enseignants et Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in (UserRole.TEACHER, UserRole.ADMIN) or request.user.is_superuser


class IsCourseOwnerOrAdmin(BasePermission):
    """
    Accès objet : Un enseignant ne peut modifier que ses propres cours.
    Un administrateur peut tout modifier.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in (UserRole.TEACHER, UserRole.ADMIN) or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == UserRole.ADMIN or request.user.is_superuser:
            return True

        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        elif hasattr(obj, 'course'):
            return obj.course.teacher == request.user
        elif hasattr(obj, 'chapter'):
            return obj.chapter.course.teacher == request.user
        return False
