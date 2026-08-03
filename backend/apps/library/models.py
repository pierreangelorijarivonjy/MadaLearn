from django.db import models
from categories.models import Category


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Titre")
    author = models.CharField(max_length=255, verbose_name="Auteur")
    description = models.TextField(blank=True, verbose_name="Description")
    cover = models.ImageField(upload_to='covers/', null=True, blank=True, verbose_name="Image de couverture")
    file = models.FileField(upload_to='books/', null=True, blank=True, verbose_name="Fichier du livre (PDF/EPUB)")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name="Catégorie"
    )
    year = models.IntegerField(null=True, blank=True, verbose_name="Année de publication")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author}"
