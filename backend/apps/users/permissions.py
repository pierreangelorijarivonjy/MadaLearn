from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import UserRole


class IsSuperAdminUser(BasePermission):
    """
    Permission accordée uniquement aux super administrateurs.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)


class IsAdminUser(BasePermission):
    """
    Permission accordée uniquement aux administrateurs (ou super admins).
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


class IsParentUser(BasePermission):
    """
    Permission accordée aux parents.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_parent)


class IsModeratorUser(BasePermission):
    """
    Permission accordée aux modérateurs (et admins).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_moderator or request.user.is_admin)
        )


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
