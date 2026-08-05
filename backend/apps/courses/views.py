from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from courses.models import Course, Chapter, Lesson
from courses.serializers import CourseSerializer, ChapterSerializer, LessonSerializer
from core.permissions import IsCourseOwnerOrAdmin


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des Cours.
    - Liste & détails des cours
    - Filtrage par catégorie, niveau et enseignant
    - Recherche par titre et description
    """
    queryset = Course.objects.all().select_related('teacher', 'category').prefetch_related('chapters__lessons').order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [IsCourseOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'teacher']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        course = self.get_object()
        chapters = course.chapters.all()
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data)


class ChapterViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des Chapitres de cours.
    """
    queryset = Chapter.objects.all().select_related('course').prefetch_related('lessons')
    serializer_class = ChapterSerializer
    permission_classes = [IsCourseOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course']
    search_fields = ['title']

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        chapter = self.get_object()
        lessons = chapter.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des Leçons.
    """
    queryset = Lesson.objects.all().select_related('chapter__course')
    serializer_class = LessonSerializer
    permission_classes = [IsCourseOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['chapter', 'chapter__course']
    search_fields = ['title', 'content']
