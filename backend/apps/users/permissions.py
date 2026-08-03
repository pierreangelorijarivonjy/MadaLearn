from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import UserRole


class IsAdminUser(BasePermission):
    """
    Permission accordée uniquement aux administrateurs.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsTeacherUser(BasePermission):
    """
    Permission accordée aux enseignants (et aux admins).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_teacher or request.user.is_admin)
        )


class IsStudentUser(BasePermission):
    """
    Permission accordée aux étudiants.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)


class IsTeacherOrReadOnly(BasePermission):
    """
    Lecture autorisée à tous les utilisateurs authentifiés, écriture aux Enseignants/Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_teacher or request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """
    Lecture autorisée à tous les utilisateurs authentifiés, écriture aux Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin
