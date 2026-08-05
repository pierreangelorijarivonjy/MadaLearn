from rest_framework import serializers
from activity.models import StudentProgress, LessonProgress, ActivityLog
from courses.models import Course, Lesson
from courses.serializers import CourseSerializer
from users.serializers import UserProfileSerializer


class ActivityLogSerializer(serializers.ModelSerializer):
    user_detail = UserProfileSerializer(source='user', read_only=True)

    class Meta:
        model = ActivityLog
        fields = (
            'id',
            'user',
            'user_detail',
            'action',
            'module',
            'description',
            'ip_address',
            'user_agent',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')


class StudentProgressSerializer(serializers.ModelSerializer):
    student_detail = UserProfileSerializer(source='student', read_only=True)
    course_detail = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = StudentProgress
        fields = (
            'id',
            'student',
            'student_detail',
            'course',
            'course_detail',
            'percentage',
            'completed',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'student', 'created_at', 'updated_at')


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = (
            'id',
            'student',
            'lesson',
            'completed',
            'completed_at'
        )
        read_only_fields = ('id', 'student', 'completed_at')
