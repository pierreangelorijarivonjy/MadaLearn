from rest_framework import serializers
from library.models import Book
from categories.models import Category
from categories.serializers import CategorySerializer


class BookSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'author',
            'description',
            'cover',
            'pdf_file',
            'language',
            'category',
            'category_detail',
            'year',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')
