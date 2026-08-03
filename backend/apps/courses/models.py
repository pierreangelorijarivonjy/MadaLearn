from django.db import models
from django.conf import settings
from categories.models import Category


class CourseLevel(models.TextChoices):
    BEGINNER = 'BEGINNER', 'Débutant'
    INTERMEDIATE = 'INTERMEDIATE', 'Intermédiaire'
    ADVANCED = 'ADVANCED', 'Avancé'


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Titre du cours")
    description = models.TextField(verbose_name="Description du cours")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name="Enseignant"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name="Catégorie"
    )
    level = models.CharField(
        max_length=20,
        choices=CourseLevel.choices,
        default=CourseLevel.BEGINNER,
        verbose_name="Niveau"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Chapter(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name="Cours"
    )
    title = models.CharField(max_length=255, verbose_name="Titre du chapitre")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Chapitre"
        verbose_name_plural = "Chapitres"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Chapitre"
    )
    title = models.CharField(max_length=255, verbose_name="Titre de la leçon")
    content = models.TextField(verbose_name="Contenu textuel / Pédagogique")
    video_url = models.URLField(blank=True, null=True, verbose_name="Lien vidéo (optionnel)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"
        ordering = ['id']

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"
