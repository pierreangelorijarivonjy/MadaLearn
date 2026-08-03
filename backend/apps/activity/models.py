from django.db import models
from django.conf import settings
from courses.models import Course


class Progress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='progresses',
        verbose_name="Étudiant"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='student_progresses',
        verbose_name="Cours"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Pourcentage d'avancement"
    )
    completed = models.BooleanField(default=False, verbose_name="Cours terminé ?")
    completed = models.BooleanField(default=False, verbose_name="Cours terminé ?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Progression"
        verbose_name_plural = "Progressions"
        unique_together = ('student', 'course')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.percentage}%)"
