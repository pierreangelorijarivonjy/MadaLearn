from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, UserRole
from courses.models import Course, Chapter, Lesson


class CourseAPITests(APITestCase):
    def setUp(self):
        self.teacher1 = User.objects.create_user(username='teacher1', password='password123', role=UserRole.TEACHER, email='t1@test.mg')
        self.teacher2 = User.objects.create_user(username='teacher2', password='password123', role=UserRole.TEACHER, email='t2@test.mg')
        self.student = User.objects.create_user(username='student1', password='password123', role=UserRole.STUDENT, email='s1@test.mg')

        self.course = Course.objects.create(
            title='Algorithmique de base',
            description='Introduction aux algorithmes',
            teacher=self.teacher1,
            level='BEGINNER'
        )

    def test_create_course(self):
        self.client.force_authenticate(user=self.teacher1)
        url = reverse('course-list')
        data = {
            'title': 'Python Avancé',
            'description': 'Cours complet sur Python',
            'level': 'ADVANCED'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['teacher'], self.teacher1.id)

    def test_update_other_teacher_course_forbidden(self):
        self.client.force_authenticate(user=self.teacher2)
        url = reverse('course-detail', kwargs={'pk': self.course.id})
        data = {'title': 'Titre modifié par Enseignant 2'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('course-list')
        data = {'title': 'Cours Etudiant', 'description': 'desc'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
