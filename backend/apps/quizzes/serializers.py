from rest_framework import serializers
from quizzes.models import Quiz, Question, Answer, QuizAttempt, StudentAnswer
from courses.models import Course


class AnswerCreateSerializer(serializers.Serializer):
    answer_text = serializers.CharField(max_length=255)
    is_correct = serializers.BooleanField(default=False)


class QuestionCreateSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    order = serializers.IntegerField(default=1)
    answers = AnswerCreateSerializer(many=True)

    def validate_answers(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('Chaque question doit contenir au moins deux réponses.')
        return value

    def validate(self, data):
        if not any(answer.get('is_correct') for answer in data['answers']):
            raise serializers.ValidationError('Chaque question doit avoir au moins une réponse correcte.')
        return data


class QuizCreateSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    questions = QuestionCreateSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ('course', 'title', 'description', 'duration', 'passing_score', 'questions')

    def validate_questions(self, value):
        if not value:
            raise serializers.ValidationError('Le quiz doit contenir au moins une question.')
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop('answers', [])
            question = Question.objects.create(quiz=quiz, **question_data)
            answers = [Answer(question=question, **answer_data) for answer_data in answers_data]
            Answer.objects.bulk_create(answers)

        return quiz


class AnswerPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer_text')


class AnswerPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer_text', 'is_correct')


class QuestionPublicSerializer(serializers.ModelSerializer):
    answers = AnswerPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'quiz', 'question_text', 'order', 'answers')


class QuestionPrivateSerializer(serializers.ModelSerializer):
    answers = AnswerPrivateSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'quiz', 'question_text', 'order', 'answers')


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('id', 'course', 'title', 'description', 'duration', 'passing_score')


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'course', 'title', 'description', 'duration', 'passing_score', 'questions')


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizListSerializer(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ('id', 'student', 'quiz', 'score', 'passed', 'started_at', 'finished_at')


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ('id', 'attempt', 'question', 'answer')


class QuizSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Dictionnaire {'question_id': 'answer_id'} contenant les réponses."
    )
