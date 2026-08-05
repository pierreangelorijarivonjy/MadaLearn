from django.db import models
from django.conf import settings
from courses.models import Course, Lesson


class ActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name="Utilisateur"
    )
    action = models.CharField(max_length=80, verbose_name="Action")
    module = models.CharField(max_length=60, verbose_name="Module")
    description = models.TextField(blank=True, default='', verbose_name="Description")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, default='', verbose_name="User-Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Journal d’activité'
        verbose_name_plural = 'Journaux d’activité'

    def __str__(self):
        return f"{self.user} - {self.action} ({self.module})"


class StudentProgress(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Progression étudiante"
        verbose_name_plural = "Progressions étudiantes"
        unique_together = ('student', 'course')
        ordering = ['-updated_at']

    def update_percentage(self):
        from courses.models import Lesson
        total_lessons = Lesson.objects.filter(chapter__course=self.course).count()
        if total_lessons == 0:
            self.percentage = 100
            self.completed = True
        else:
            completed_lessons = LessonProgress.objects.filter(
                student=self.student,
                lesson__chapter__course=self.course,
                completed=True
            ).count()
            self.percentage = round((completed_lessons / total_lessons) * 100, 2)
            self.completed = (self.percentage >= 100)
        self.save()

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.percentage}%)"


class LessonProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progresses',
        verbose_name="Étudiant"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name="Leçon"
    )
    completed = models.BooleanField(default=False, verbose_name="Leçon terminée ?")
    completed_at = models.DateTimeField(auto_now=True, verbose_name="Date de complétion")

    class Meta:
        verbose_name = "Progression leçon"
        verbose_name_plural = "Progressions leçons"
        unique_together = ('student', 'lesson')
        ordering = ['-completed_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_parent_progress()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_parent_progress()

    def update_parent_progress(self):
        progress, created = StudentProgress.objects.get_or_create(
            student=self.student,
            course=self.lesson.chapter.course
        )
        progress.update_percentage()

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title} ({'Terminée' if self.completed else 'En cours'})"
