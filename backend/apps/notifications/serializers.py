from rest_framework import serializers, viewsets, permissions
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'user', 'title', 'message', 'is_read', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la consultation des notifications de l'utilisateur connecté.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
