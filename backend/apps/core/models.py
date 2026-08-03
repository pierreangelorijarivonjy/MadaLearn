from django.db import models


class TimeStampedModel(models.Model):
    """
    Classe abstraite ajoutant les horodatages created_at et updated_at.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        abstract = True
