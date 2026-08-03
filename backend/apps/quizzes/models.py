from django.db import models
from courses.models import Course


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Cours"
    )
    title = models.CharField(max_length=255, verbose_name="Titre du quiz")
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

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
