from django.urls import path
from rest_framework.routers import DefaultRouter
from activity.views import ProgressViewSet, CourseProgressView, CompleteLessonView, UncompleteLessonView, ActivityLogViewSet

router = DefaultRouter()
router.register(r'progress', ProgressViewSet, basename='progress')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')

urlpatterns = [
    path('courses/<int:course_id>/progress/', CourseProgressView.as_view(), name='course-progress'),
    path('lessons/<int:id>/complete/', CompleteLessonView.as_view(), name='lesson-complete'),
    path('lessons/<int:id>/uncomplete/', UncompleteLessonView.as_view(), name='lesson-uncomplete'),
] + router.urls
