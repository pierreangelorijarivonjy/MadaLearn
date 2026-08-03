from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from activity.models import Progress
from activity.serializers import ProgressSerializer


class ProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion et la consultation de la progression des étudiants.
    - Étudiant : accède à ses propres progressions.
    - Enseignant : accède aux progressions des étudiants inscrits à ses cours.
    - Admin : accède à l'ensemble des progressions.
    """
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'completed', 'student']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Progress.objects.none()

        if user.is_admin:
            return Progress.objects.all().select_related('student', 'course')
        elif user.is_teacher:
            return Progress.objects.filter(course__teacher=user).select_related('student', 'course')
        else:
            return Progress.objects.filter(student=user).select_related('student', 'course')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
