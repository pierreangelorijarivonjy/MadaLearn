from rest_framework.routers import DefaultRouter
from quizzes.views import QuizViewSet, QuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerViewSet, basename='answer')

urlpatterns = router.urls
