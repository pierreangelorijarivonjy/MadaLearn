from rest_framework import serializers
from quizzes.models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer_text', 'is_correct')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'quiz', 'question_text', 'answers')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'course', 'title', 'questions')


class QuizSubmissionSerializer(serializers.Serializer):
    selected_answer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Liste des ID des réponses sélectionnées par l'étudiant."
    )
