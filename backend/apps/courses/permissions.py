from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCourseOwnerOrAdmin(BasePermission):
    """
    Lecture accessible à tous les utilisateurs authentifiés.
    Modification/Suppression réservée à l'enseignant propriétaire du cours ou à un Admin.
    """
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
        
        # Check course ownership
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        elif hasattr(obj, 'course'):
            return obj.course.teacher == request.user
        elif hasattr(obj, 'chapter'):
            return obj.chapter.course.teacher == request.user
        return False
