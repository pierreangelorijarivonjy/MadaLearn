from rest_framework import serializers
from courses.models import Course, Chapter, Lesson
from categories.models import Category
from categories.serializers import CategorySerializer
from users.serializers import UserProfileSerializer


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'chapter', 'title', 'content', 'video_url', 'pdf', 'duration', 'order')


class ChapterSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ('id', 'course', 'title', 'order', 'lessons')


class CourseSerializer(serializers.ModelSerializer):
    teacher_detail = UserProfileSerializer(source='teacher', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'description',
            'thumbnail',
            'teacher',
            'teacher_detail',
            'category',
            'category_detail',
            'level',
            'status',
            'created_at',
            'chapters'
        )
        read_only_fields = ('id', 'teacher', 'created_at')
