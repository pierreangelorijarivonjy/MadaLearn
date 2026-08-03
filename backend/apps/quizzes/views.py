from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from quizzes.models import Quiz, Question, Answer
from quizzes.serializers import (
    QuizSerializer,
    QuestionSerializer,
    AnswerSerializer,
    QuizSubmissionSerializer
)
from core.permissions import IsTeacherOrReadOnly
from activity.models import Progress


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des Quizs et leur évaluation.
    """
    queryset = Quiz.objects.all().select_related('course').prefetch_related('questions__answers')
    serializer_class = QuizSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], serializer_class=QuizSubmissionSerializer)
    def submit(self, request, pk=None):
        """
        Soumettre des réponses à un Quiz et calculer le résultat.
        Met également à jour la progression de l'étudiant pour ce cours.
        """
        quiz = self.get_object()
        serializer = QuizSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selected_ids = serializer.validated_data['selected_answer_ids']
        questions = quiz.questions.prefetch_related('answers').all()

        total_questions = questions.count()
        if total_questions == 0:
            return Response({"detail": "Ce quiz ne contient aucune question."}, status=status.HTTP_400_BAD_REQUEST)

        correct_count = 0
        details = []

        for question in questions:
            correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
            user_selected_for_q = set(selected_ids).intersection(set(question.answers.values_list('id', flat=True)))
            
            is_q_correct = (user_selected_for_q == correct_answers and len(correct_answers) > 0)
            if is_q_correct:
                correct_count += 1

            details.append({
                "question_id": question.id,
                "question_text": question.question_text,
                "correct": is_q_correct,
                "user_selected": list(user_selected_for_q),
                "correct_answers": list(correct_answers)
            })

        percentage = round((correct_count / total_questions) * 100, 2)
        completed = percentage >= 70.0  # 70% pour réussir le quiz

        # Mettre à jour la progression si l'utilisateur est un étudiant
        progress_obj = None
        if request.user.is_student or request.user.is_authenticated:
            progress_obj, _ = Progress.objects.get_or_create(
                student=request.user,
                course=quiz.course,
                defaults={'percentage': percentage, 'completed': completed}
            )
            if percentage > float(progress_obj.percentage):
                progress_obj.percentage = percentage
                progress_obj.completed = completed or progress_obj.completed
                progress_obj.save()

        return Response({
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "score": correct_count,
            "total_questions": total_questions,
            "percentage": percentage,
            "passed": completed,
            "details": details
        }, status=status.HTTP_200_OK)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().select_related('quiz').prefetch_related('answers')
    serializer_class = QuestionSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz']


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all().select_related('question')
    serializer_class = AnswerSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']
