from django.db import models
from django.conf import settings


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='notifications',
        verbose_name="Destinataire"
    )
    title = models.CharField(max_length=255, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu ?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
