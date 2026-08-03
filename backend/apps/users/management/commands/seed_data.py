from django.core.management.base import BaseCommand
from users.models import User, UserRole
from categories.models import Category
from library.models import Book
from courses.models import Course, Chapter, Lesson, CourseLevel
from quizzes.models import Quiz, Question, Answer
from activity.models import Progress


class Command(BaseCommand):
    help = "Remplit la base de données avec des données initiales de démonstration pour MadaLearn."

    def handle(self, *args, **options):
        self.stdout.write("Création des utilisateurs...")

        # 1. Users
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@madalearn.mg',
                'first_name': 'Admin',
                'last_name': 'MadaLearn',
                'role': UserRole.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin1234')
        admin_user.save()

        teacher_user, _ = User.objects.get_or_create(
            username='enseignant',
            defaults={
                'email': 'teacher@madalearn.mg',
                'first_name': 'Hery',
                'last_name': 'Rakoto',
                'role': UserRole.TEACHER
            }
        )
        teacher_user.set_password('teacher1234')
        teacher_user.save()

        student_user, _ = User.objects.get_or_create(
            username='etudiant',
            defaults={
                'email': 'student@madalearn.mg',
                'first_name': 'Soa',
                'last_name': 'Rasoa',
                'role': UserRole.STUDENT
            }
        )
        student_user.set_password('student1234')
        student_user.save()

        # 2. Categories
        cat_math, _ = Category.objects.get_or_create(
            name='Mathématiques',
            defaults={'description': 'Cours et ouvrages de mathématiques pour tous les niveaux.'}
        )
        cat_info, _ = Category.objects.get_or_create(
            name='Informatique',
            defaults={'description': 'Algorithmique, développement web et technologies numériques.'}
        )
        cat_hist, _ = Category.objects.get_or_create(
            name='Histoire & Culture',
            defaults={'description': 'Histoire de Madagascar, patrimoine et langues.'}
        )

        # 3. Books
        Book.objects.get_or_create(
            title='Informatique et Numérique à Madagascar',
            defaults={
                'author': 'Hery Rakoto',
                'description': 'Introduction aux compétences numériques essentielles.',
                'category': cat_info,
                'year': 2024
            }
        )
        Book.objects.get_or_create(
            title='Mathématiques Fondamentales - Collège',
            defaults={
                'author': 'Dr Jean Rabe',
                'description': 'Algèbre et géométrie pour les classes du secondaire.',
                'category': cat_math,
                'year': 2023
            }
        )

        # 4. Courses & Chapters
        course, _ = Course.objects.get_or_create(
            title='Introduction au Développement Web avec Python',
            defaults={
                'description': 'Apprenez les bases de la programmation web avec Python et Django.',
                'teacher': teacher_user,
                'category': cat_info,
                'level': CourseLevel.BEGINNER
            }
        )

        ch1, _ = Chapter.objects.get_or_create(
            course=course,
            title='Chapitre 1 : Les bases de Python',
            defaults={'order': 1}
        )
        Lesson.objects.get_or_create(
            chapter=ch1,
            title='Leçon 1 : Variables et Types de données',
            defaults={
                'content': 'En Python, les variables sont créées au moment où vous leur attribuez une valeur...',
                'video_url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8'
            }
        )

        ch2, _ = Chapter.objects.get_or_create(
            course=course,
            title='Chapitre 2 : Introduction aux API REST',
            defaults={'order': 2}
        )
        Lesson.objects.get_or_create(
            chapter=ch2,
            title='Leçon 1 : Qu\'est-ce qu\'une API REST ?',
            defaults={
                'content': 'REST signifie Representational State Transfer. C\'est un style d\'architecture pour la conception d\'applications réseau...',
            }
        )

        # 5. Quiz
        quiz, _ = Quiz.objects.get_or_create(
            course=course,
            title='Quiz 1 : Les fondamentaux de Python'
        )

        q1, _ = Question.objects.get_or_create(
            quiz=quiz,
            question_text='Quelle est l\'extension standard des fichiers Python ?'
        )
        Answer.objects.get_or_create(question=q1, answer_text='.py', defaults={'is_correct': True})
        Answer.objects.get_or_create(question=q1, answer_text='.js', defaults={'is_correct': False})
        Answer.objects.get_or_create(question=q1, answer_text='.html', defaults={'is_correct': False})

        q2, _ = Question.objects.get_or_create(
            quiz=quiz,
            question_text='Quel mot-clé est utilisé pour définir une fonction en Python ?'
        )
        Answer.objects.get_or_create(question=q2, answer_text='func', defaults={'is_correct': False})
        Answer.objects.get_or_create(question=q2, answer_text='def', defaults={'is_correct': True})
        Answer.objects.get_or_create(question=q2, answer_text='function', defaults={'is_correct': False})

        # 6. Progress
        Progress.objects.get_or_create(
            student=student_user,
            course=course,
            defaults={'percentage': 50.00, 'completed': False}
        )

        self.stdout.write(self.style.SUCCESS("Base de données initialisée avec succès !"))
        self.stdout.write(self.style.SUCCESS("Comptes créés :"))
        self.stdout.write(" - Admin: admin / admin1234")
        self.stdout.write(" - Enseignant: enseignant / teacher1234")
        self.stdout.write(" - Etudiant: etudiant / student1234")
