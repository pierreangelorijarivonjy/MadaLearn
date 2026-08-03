from rest_framework import serializers
from activity.models import Progress
from courses.models import Course
from courses.serializers import CourseSerializer
from users.serializers import UserProfileSerializer


class ProgressSerializer(serializers.ModelSerializer):
    student_detail = UserProfileSerializer(source='student', read_only=True)
    course_detail = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Progress
        fields = (
            'id',
            'student',
            'student_detail',
            'course',
            'course_detail',
            'percentage',
            'completed',
            'updated_at'
        )
        read_only_fields = ('id', 'student', 'updated_at')
