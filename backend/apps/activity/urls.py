from rest_framework.routers import DefaultRouter
from activity.views import ProgressViewSet

router = DefaultRouter()
router.register(r'progress', ProgressViewSet, basename='progress')

urlpatterns = router.urls
