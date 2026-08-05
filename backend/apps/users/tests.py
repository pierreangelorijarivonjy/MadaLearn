from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, UserRole, Role, Permission, RolePermission, UserStatus, User as UserModel
from activity.models import ActivityLog


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


class RbacAndAuditTests(APITestCase):
    def setUp(self):
        self.admin = UserModel.objects.create_user(
            username='adminrbac',
            email='adminrbac@madalearn.mg',
            password='StrongPass123',
            role=UserRole.ADMIN,
            first_name='Admin',
            last_name='RBAC'
        )
        self.student = UserModel.objects.create_user(
            username='studentrbac',
            email='studentrbac@madalearn.mg',
            password='StrongPass123',
            role=UserRole.STUDENT,
            first_name='Student',
            last_name='RBAC'
        )
        self.role = Role.objects.create(code='students.read', name='Lecture étudiants', description='Lecture des étudiants')
        self.permission = Permission.objects.create(code='users.read', module='users', name='Consulter les utilisateurs')
        RolePermission.objects.create(role=self.role, permission=self.permission)
        self.admin.roles.add(self.role)
        self.client.force_authenticate(user=self.admin)

    def test_soft_delete_and_status_change(self):
        self.student.soft_delete()
        self.assertEqual(self.student.status, UserStatus.DELETED)
        self.assertFalse(self.student.is_active)
        self.assertIsNotNone(self.student.deleted_at)

    def test_has_permission_from_role(self):
        self.assertTrue(self.admin.has_permission('users.read'))
        self.assertFalse(self.student.has_permission('users.read'))

    def test_activity_log_is_created(self):
        ActivityLog.objects.create(
            user=self.admin,
            action='login',
            module='auth',
            description='Connexion utilisateur',
            ip_address='127.0.0.1',
            user_agent='test-agent'
        )
        self.assertTrue(ActivityLog.objects.filter(user=self.admin, action='login').exists())
