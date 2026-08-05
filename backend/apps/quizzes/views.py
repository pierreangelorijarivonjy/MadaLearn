from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from quizzes.models import Quiz, Question, Answer, QuizAttempt, StudentAnswer
from quizzes.serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuestionPublicSerializer,
    QuestionPrivateSerializer,
    AnswerPublicSerializer,
    AnswerPrivateSerializer,
    QuizCreateSerializer,
    QuizAttemptSerializer,
    QuizSubmitSerializer
)
from core.permissions import IsTeacherOrReadOnly
from activity.models import StudentProgress


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des Quizs et leur évaluation.
    """
    queryset = Quiz.objects.all().select_related('course').prefetch_related('questions__answers')
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        if self.action == 'create':
            return QuizCreateSerializer
        return QuizDetailSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='my-quizzes')
    def my_quizzes(self, request):
        """
        Lister les tentatives de quiz de l'étudiant.
        """
        attempts = QuizAttempt.objects.filter(student=request.user).select_related('quiz')
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def start(self, request, pk=None):
        """
        Démarrer un quiz. Renvoie l'ID de la tentative.
        """
        quiz = self.get_object()
        
        # Vérifier si l'étudiant a déjà une tentative en cours ou s'il a déjà réussi ?
        # "Une tentative à la fois." -> S'il y a une tentative non terminée, on la renvoie.
        active_attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz, finished_at__isnull=True).first()
        if active_attempt:
            # Vérifier si le temps n'est pas écoulé
            elapsed = (timezone.now() - active_attempt.started_at).total_seconds() / 60
            if elapsed > quiz.duration:
                active_attempt.finished_at = timezone.now()
                active_attempt.score = 0
                active_attempt.passed = False
                active_attempt.save()
            else:
                return Response({
                    "attempt_id": active_attempt.id,
                    "started_at": active_attempt.started_at,
                    "quiz": QuizDetailSerializer(quiz).data
                }, status=status.HTTP_200_OK)

        # Créer une nouvelle tentative
        attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz)
        return Response({
            "attempt_id": attempt.id,
            "started_at": attempt.started_at,
            "quiz": QuizDetailSerializer(quiz).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], serializer_class=QuizSubmitSerializer)
    def submit(self, request, pk=None):
        """
        Soumettre des réponses à un Quiz et calculer le résultat.
        """
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_answers = serializer.validated_data['answers']
        
        # Récupérer la tentative active la plus récente
        attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz, finished_at__isnull=True).order_by('-started_at').first()
        if not attempt:
            return Response({"detail": "Aucune tentative en cours trouvée."}, status=status.HTTP_400_BAD_REQUEST)

        questions = quiz.questions.prefetch_related('answers').all()
        total_questions = questions.count()
        if total_questions == 0:
            return Response({"detail": "Ce quiz ne contient aucune question."}, status=status.HTTP_400_BAD_REQUEST)

        correct_count = 0

        for question in questions:
            correct_answer = question.answers.filter(is_correct=True).first() # On suppose une seule bonne réponse pour simplifier le front pour l'instant (les QCM multiples sont plus complexes à noter uniformément)
            # Ou on peut vérifier si selected_id == correct_id
            selected_id = user_answers.get(str(question.id))
            
            if selected_id:
                try:
                    answer_obj = question.answers.get(id=selected_id)
                    StudentAnswer.objects.create(attempt=attempt, question=question, answer=answer_obj)
                    if answer_obj.is_correct:
                        correct_count += 1
                except Answer.DoesNotExist:
                    pass

        percentage = round((correct_count / total_questions) * 100, 2)
        passed = percentage >= quiz.passing_score
        
        attempt.finished_at = timezone.now()
        attempt.score = percentage
        attempt.passed = passed
        attempt.save()

        # Mettre à jour la progression
        if passed:
            progress_obj, _ = StudentProgress.objects.get_or_create(
                student=request.user,
                course=quiz.course,
                defaults={'percentage': 100, 'completed': True}
            )
            progress_obj.percentage = 100
            progress_obj.completed = True
            progress_obj.save()

        return Response({
            "attempt_id": attempt.id,
            "score": correct_count,
            "total_questions": total_questions,
            "percentage": percentage,
            "passed": passed
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def result(self, request, pk=None):
        """
        Voir le dernier résultat (avec corrections).
        """
        quiz = self.get_object()
        attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz, finished_at__isnull=False).order_by('-finished_at').first()
        
        if not attempt:
            return Response({"detail": "Aucun résultat trouvé."}, status=status.HTTP_404_NOT_FOUND)
            
        student_answers = {sa.question_id: sa.answer_id for sa in attempt.student_answers.all()}
        
        questions = quiz.questions.prefetch_related('answers').all()
        details = []
        
        for q in questions:
            correct_ans = q.answers.filter(is_correct=True).first()
            selected_ans_id = student_answers.get(q.id)
            details.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "correct_answer_id": correct_ans.id if correct_ans else None,
                "user_answer_id": selected_ans_id,
                "is_correct": selected_ans_id == (correct_ans.id if correct_ans else None),
                "answers": AnswerPublicSerializer(q.answers.all(), many=True).data # Retourner les options pour affichage
            })
            
        return Response({
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "attempt": QuizAttemptSerializer(attempt).data,
            "details": details
        }, status=status.HTTP_200_OK)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().select_related('quiz').prefetch_related('answers')
    serializer_class = QuestionPrivateSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz']


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all().select_related('question')
    serializer_class = AnswerPrivateSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']
