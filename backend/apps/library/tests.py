from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, UserRole
from categories.models import Category
from library.models import Book


class LibraryAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Sciences', description='Livres scientifiques')
        self.student = User.objects.create_user(username='student', password='password123', role=UserRole.STUDENT, email='s@test.mg')
        self.teacher = User.objects.create_user(username='teacher', password='password123', role=UserRole.TEACHER, email='t@test.mg')

        self.book1 = Book.objects.create(
            title='Physique Chimie 3ème',
            author='Prof Rakoto',
            description='Manuel de physique',
            category=self.category,
            year=2023
        )
        self.book2 = Book.objects.create(
            title='Histoire de Madagascar',
            author='Dr Rasoa',
            description='Livre d\'histoire',
            year=2021
        )

    def test_list_books(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_search_book_by_title(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('book-list') + '?search=Physique'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Physique Chimie 3ème')

    def test_filter_book_by_category(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('book-list') + f'?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_book_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('book-list')
        data = {'title': 'Nouveau Livre', 'author': 'Auteur X'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('book-list')
        data = {'title': 'Nouveau Livre Pédagogique', 'author': 'Prof Teacher', 'category': self.category.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
