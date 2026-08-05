from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import OperationalError, ProgrammingError
from django_filters.rest_framework import DjangoFilterBackend

from activity.models import StudentProgress, LessonProgress, ActivityLog
from activity.serializers import StudentProgressSerializer, LessonProgressSerializer, ActivityLogSerializer
from courses.models import Lesson, Course
from users.models import UserStatus


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'module', 'action']
    search_fields = ['description', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return ActivityLog.objects.select_related('user').all()
        return ActivityLog.objects.select_related('user').filter(user=user)


class ProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion et la consultation de la progression des étudiants.
    """
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'completed', 'student']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return StudentProgress.objects.none()

        try:
            if user.is_admin:
                return StudentProgress.objects.all().select_related('student', 'course')
            elif getattr(user, 'is_teacher', False):
                return StudentProgress.objects.filter(course__teacher=user).select_related('student', 'course')
            else:
                return StudentProgress.objects.filter(student=user).select_related('student', 'course')
        except (OperationalError, ProgrammingError):
            return StudentProgress.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except (OperationalError, ProgrammingError):
            return Response([], status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except (OperationalError, ProgrammingError):
            return Response({
                'id': None,
                'student': request.user.id,
                'course': None,
                'percentage': 0,
                'completed': False,
                'created_at': None,
                'updated_at': None,
            }, status=status.HTTP_200_OK)


class CourseProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        try:
            progress, created = StudentProgress.objects.get_or_create(
                student=request.user,
                course=course
            )

            completed_lessons = LessonProgress.objects.filter(
                student=request.user,
                lesson__chapter__course=course,
                completed=True
            )

            return Response({
                'progress': StudentProgressSerializer(progress).data,
                'completed_lessons': [lp.lesson.id for lp in completed_lessons]
            })
        except (OperationalError, ProgrammingError):
            return Response({
                'progress': {
                    'id': None,
                    'student': request.user.id,
                    'course': course.id,
                    'percentage': 0,
                    'completed': False,
                    'created_at': None,
                    'updated_at': None,
                },
                'completed_lessons': []
            }, status=status.HTTP_200_OK)


class CompleteLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        lesson = get_object_or_404(Lesson, id=id)
        try:
            progress, created = LessonProgress.objects.get_or_create(
                student=request.user,
                lesson=lesson
            )
            if not progress.completed:
                progress.completed = True
                progress.save()

            course_progress = StudentProgress.objects.filter(student=request.user, course=lesson.chapter.course).first()

            return Response({
                'detail': 'Leçon terminée',
                'course_percentage': course_progress.percentage if course_progress else 0
            })
        except (OperationalError, ProgrammingError):
            return Response({
                'detail': 'Leçon terminée',
                'course_percentage': 0
            }, status=status.HTTP_200_OK)


class UncompleteLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        lesson = get_object_or_404(Lesson, id=id)
        try:
            progress = LessonProgress.objects.filter(
                student=request.user,
                lesson=lesson
            ).first()

            if progress and progress.completed:
                progress.completed = False
                progress.save()

            course_progress = StudentProgress.objects.filter(student=request.user, course=lesson.chapter.course).first()

            return Response({
                'detail': 'Progression annulée pour cette leçon',
                'course_percentage': course_progress.percentage if course_progress else 0
            })
        except (OperationalError, ProgrammingError):
            return Response({
                'detail': 'Progression annulée pour cette leçon',
                'course_percentage': 0
            }, status=status.HTTP_200_OK)
