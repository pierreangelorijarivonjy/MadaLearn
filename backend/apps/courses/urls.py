from rest_framework.routers import DefaultRouter
from courses.views import CourseViewSet, ChapterViewSet, LessonViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'lessons', LessonViewSet, basename='lesson')

urlpatterns = router.urls
