from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, UserRole


class UserAuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.token_url = reverse('token-obtain-pair')
        self.profile_url = reverse('user-profile')

        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@madalearn.mg',
            password='password123',
            role=UserRole.STUDENT
        )

        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@madalearn.mg',
            password='password123',
            role=UserRole.TEACHER
        )

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@madalearn.mg',
            'password': 'StrongPassword123',
            'first_name': 'Jean',
            'last_name': 'Rabe',
            'role': 'STUDENT'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_jwt_login(self):
        data = {
            'username': 'student1',
            'password': 'password123'
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_access(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'student1')
        self.assertEqual(response.data['role'], 'STUDENT')
