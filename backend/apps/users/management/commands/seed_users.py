import os
from django.core.management.base import BaseCommand
from users.models import User, UserRole

class Command(BaseCommand):
    help = 'Génère des utilisateurs de démonstration pour chaque rôle RBAC.'

    def handle(self, *args, **kwargs):
        users_data = [
            {'username': 'superadmin', 'email': 'superadmin@madalearn.com', 'role': UserRole.SUPER_ADMIN},
            {'username': 'admin', 'email': 'admin@madalearn.com', 'role': UserRole.ADMIN},
            {'username': 'teacher', 'email': 'teacher@madalearn.com', 'role': UserRole.TEACHER},
            {'username': 'student', 'email': 'student@madalearn.com', 'role': UserRole.STUDENT},
            {'username': 'parent', 'email': 'parent@madalearn.com', 'role': UserRole.PARENT},
            {'username': 'moderator', 'email': 'moderator@madalearn.com', 'role': UserRole.MODERATOR},
        ]
        
        password = 'MadaLearn2026!'
        
        for data in users_data:
            username = data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=data['email'],
                    password=password,
                    role=data['role']
                )
                if data['role'] == UserRole.SUPER_ADMIN:
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                self.stdout.write(self.style.SUCCESS(f'Utilisateur {username} créé avec succès (rôle: {data["role"]}).'))
            else:
                self.stdout.write(self.style.WARNING(f'L\'utilisateur {username} existe déjà.'))
                
        self.stdout.write(self.style.SUCCESS('Les données de démonstration des utilisateurs ont été initialisées !'))
