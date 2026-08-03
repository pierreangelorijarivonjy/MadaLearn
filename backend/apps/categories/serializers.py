from rest_framework import serializers, viewsets
from categories.models import Category
from core.permissions import IsTeacherOrReadOnly


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des catégories de cours et livres.
    Lecture accessible à tous, modification réservée aux Enseignants/Admins.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsTeacherOrReadOnly]
    search_fields = ['name', 'description']
