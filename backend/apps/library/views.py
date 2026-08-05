from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from library.models import Book
from library.serializers import BookSerializer
from core.permissions import IsAdminOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la bibliothèque numérique (Livres).
    Supporte :
    - GET /api/books/ (Liste paginée des livres)
    - GET /api/books/{id}/ (Détails d'un livre)
    - POST /api/books/ (Ajout de livre - Administrateur)
    - PUT/PATCH /api/books/{id}/ (Modification - Administrateur)
    - DELETE /api/books/{id}/ (Suppression - Administrateur)
    
    Filtres disponibles :
    - ?category=<id>
    - ?year=<année>
    - ?search=<terme_recherche> (recherche par titre, auteur)
    """
    queryset = Book.objects.all().select_related('category').order_by('-created_at')
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'year']
    search_fields = ['title', 'author', 'description']
    ordering_fields = ['created_at', 'title', 'year']
