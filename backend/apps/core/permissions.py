from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import UserRole


class IsActiveUser(BasePermission):
    """Vérifie qu’un utilisateur est authentifié, actif et non supprimé."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_active', False) and
            not getattr(request.user, 'is_deleted', False)
        )


class HasPermission(BasePermission):
    """Vérifie qu’un utilisateur possède une permission RBAC précise."""
    permission_code = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not self.permission_code:
            return False
        return request.user.has_permission(self.permission_code)


class HasAnyPermission(BasePermission):
    """Vérifie qu’un utilisateur possède au moins l’une des permissions demandées."""
    permission_codes = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return any(request.user.has_permission(code) for code in self.permission_codes)


class IsSuperAdmin(BasePermission):
    """Accès exclusif Super Admin"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)


class IsAdminUser(BasePermission):
    """Accès Admins et Super Admins"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsTeacherUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_teacher)


class IsStudentUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)


class IsParentUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_parent)


class IsModeratorUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_moderator)


class IsTeacherOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_teacher or request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin


class IsCourseOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_teacher or request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_admin:
            return True

        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        elif hasattr(obj, 'course'):
            return obj.course.teacher == request.user
        elif hasattr(obj, 'chapter'):
            return obj.chapter.course.teacher == request.user
        return False
