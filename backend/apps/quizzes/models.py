from django.db import models
from django.conf import settings
from courses.models import Course


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Cours"
    )
    title = models.CharField(max_length=255, verbose_name="Titre du quiz")
    description = models.TextField(blank=True, verbose_name="Description du quiz")
    duration = models.PositiveIntegerField(default=15, help_text="Durée en minutes", verbose_name="Durée")
    passing_score = models.PositiveIntegerField(default=70, help_text="Pourcentage requis pour réussir", verbose_name="Score de passage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizs"

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Quiz"
    )
    question_text = models.TextField(verbose_name="Intitulé de la question")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre de la question")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['order', 'id']

    def __str__(self):
        return self.question_text[:50]


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Question"
    )
    answer_text = models.CharField(max_length=255, verbose_name="Texte de la réponse")
    is_correct = models.BooleanField(default=False, verbose_name="Réponse correcte ?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"

    def __str__(self):
        return f"{self.answer_text} ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name="Étudiant"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Quiz"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Score obtenu"
    )
    passed = models.BooleanField(null=True, blank=True, verbose_name="Réussi ?")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Débuté le")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminé le")

    class Meta:
        verbose_name = "Tentative de Quiz"
        verbose_name_plural = "Tentatives de Quiz"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}%"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name="Tentative"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Question"
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Réponse choisie"
    )

    class Meta:
        verbose_name = "Réponse d'étudiant"
        verbose_name_plural = "Réponses d'étudiants"
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.question_text[:20]}"
