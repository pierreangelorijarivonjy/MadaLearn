# MadaLearn - Backend API

Plateforme éducative numérique adaptée au contexte malgache.
Backend développé avec **Python 3**, **Django 5**, **Django REST Framework (DRF)**, **PostgreSQL**, et authentification **JWT (Simple JWT)**.

---

## 🛠️ Stack Technique

- **Langage** : Python 3.12+
- **Framework Web** : Django 5
- **API Framework** : Django REST Framework
- **Base de Données** : PostgreSQL 16
- **Authentification** : JWT (djangorestframework-simplejwt)
- **CORS** : django-cors-headers
- **Documentation OpenAPI/Swagger** : drf-spectacular
- **Gestion des Fichiers** : Pillow

---

## 📁 Structure du Projet

```text
backend/
├── config/                  # Configuration principale Django (settings, urls, wsgi, asgi)
├── apps/
│   ├── users/               # Custom User Model (ADMIN, TEACHER, STUDENT), Auth JWT, Permissions
│   ├── categories/          # Gestion des catégories partagées (Bibliothèque, Cours)
│   ├── library/             # Bibliothèque numérique (Livres PDF, Couvertures, Filtres & Recherche)
│   ├── courses/             # Cours, Chapitres, Leçons & Gestion Enseignant/Admin
│   ├── quizzes/             # Quizs, Questions, Réponses & Évaluation automatique des résultats
│   ├── activity/            # Suivi de la progression des étudiants par cours
│   └── notifications/      # Notifications système pour les utilisateurs
├── media/                   # Fichiers médias téléversés (couvertures, fichiers PDF)
├── .env.example             # Exemple des variables d'environnement
├── .env                     # Variables d'environnement locales
├── manage.py
├── requirements.txt         # Dépendances Python
└── README.md
```

---

## 🚀 Installation et Lancement

### 1. Prérequis
- Python 3.12+
- PostgreSQL en cours d'exécution sur `localhost:5432`

### 2. Base de Données PostgreSQL
Créer la base de données et l'utilisateur PostgreSQL :
```bash
psql -U postgres -c "CREATE DATABASE madalearn_db;"
psql -U postgres -c "CREATE USER madalearn_user WITH PASSWORD 'madalearn_pass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE madalearn_db TO madalearn_user;"
psql -d madalearn_db -c "GRANT ALL ON SCHEMA public TO madalearn_user;"
```

### 3. Environnement Virtuel & Dépendances
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. Configuration .env
Créer un fichier `.env` dans le dossier `backend/` :
```env
DATABASE_NAME=madalearn_db
DATABASE_USER=madalearn_user
DATABASE_PASSWORD=madalearn_pass
DATABASE_HOST=localhost
DATABASE_PORT=5432
SECRET_KEY=votre_secret_key_securisee
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Migrations & Initialisation des Données
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

### 6. Lancement du Serveur de Développement
```bash
python manage.py runserver
```

Le serveur sera accessible sur : `http://127.0.0.1:8000/`

---

## 🐳 Déploiement avec Docker

Pour exécuter le backend de manière isolée avec Docker et Docker Compose :

### 1. Prérequis Docker
- Docker et Docker Compose doivent être installés.

### 2. Démarrage Rapide
À la racine du dossier `backend/`, exécutez simplement :
```bash
docker compose up -d --build
```

### 3. Exécution des Migrations dans Docker
Une fois le conteneur démarré :
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_data
```

Le serveur sera alors accessible sur : `http://127.0.0.1:8000/`. Gunicorn et WhiteNoise gèrent les requêtes et fichiers statiques dans cet environnement configuré pour la production.

---

## 🌍 Déploiement en Production

1. **Variables d'Environnement** :  
   Assurez-vous de définir `DEBUG=False` dans le `.env` et de configurer `ALLOWED_HOSTS` ainsi que `CORS_ALLOWED_ORIGINS` avec les URL de production.  
   Changez impérativement la `SECRET_KEY`.

2. **Serveur WSGI et Statiques** :  
   Gunicorn est configuré comme serveur PWSGI (`gunicorn config.wsgi:application`) et WhiteNoise sert les fichiers statiques de façon optimale.

3. **HTTPS / SSL** :  
   Si le backend est derrière un proxy inverse (comme Nginx), n'oubliez pas d'activer le SSL/TLS. Les paramètres de sécurité HTTPS sont pré-configurés dans `settings.py` (comme `SECURE_SSL_REDIRECT` modifiable via `.env`).

---

## 🔑 Comptes de Démonstration (Créés par `seed_data`)

| Rôle | Nom d'utilisateur | Mot de passe | Email |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin` | `admin1234` | `admin@madalearn.mg` |
| **TEACHER** | `enseignant` | `teacher1234` | `teacher@madalearn.mg` |
| **STUDENT** | `etudiant` | `student1234` | `student@madalearn.mg` |

---

## 📖 Documentation API (Swagger / OpenAPI UI)

La documentation interactive Swagger est générée automatiquement et accessible aux URLs suivantes :

- **Swagger UI** : `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc UI** : `http://127.0.0.1:8000/api/schema/redoc/`
- **OpenAPI Schema (JSON)** : `http://127.0.0.1:8000/api/schema/`

---

## 📌 Endpoints Principaux

### 👤 Authentification et Utilisateurs (`/api/users/`)
- `POST /api/users/register/` : Inscription d'un utilisateur (ADMIN, TEACHER, STUDENT)
- `POST /api/users/token/` : Connexion JWT (retourne Access + Refresh Token + Profil)
- `POST /api/users/token/refresh/` : Rafraîchir le token Access
- `GET/PUT/PATCH /api/users/me/` : Récupérer / Modifier le profil connecté
- `GET /api/users/` : Liste de tous les utilisateurs (Admin uniquement)

### 📚 Bibliothèque Numérique (`/api/books/` & `/api/categories/`)
- `GET /api/categories/` : Liste des catégories
- `GET /api/books/` : Liste paginée des livres (filtre `?category=<id>`, `?year=<année>`, recherche `?search=titre`)
- `GET /api/books/{id}/` : Détail d'un livre
- `POST /api/books/` : Ajouter un livre (Enseignant/Admin)
- `PUT/DELETE /api/books/{id}/` : Modifier/Supprimer un livre (Enseignant/Admin)

### 🎓 Plateforme de Cours (`/api/courses/`, `/api/chapters/`, `/api/lessons/`)
- `GET /api/courses/` : Liste des cours (filtre `?category=<id>`, `?level=BEGINNER`, `?teacher=<id>`)
- `POST /api/courses/` : Créer un cours (Enseignant/Admin)
- `GET/PUT/DELETE /api/courses/{id}/` : Gestion d'un cours (Propriétaire / Admin)
- `GET/POST /api/chapters/` : Gestion des chapitres
- `GET/POST /api/lessons/` : Gestion des leçons

### 📝 Quiz et Évaluations (`/api/quizzes/`, `/api/questions/`, `/api/answers/`)
- `GET /api/quizzes/` : Liste des quiz
- `POST /api/quizzes/{id}/submit/` : Soumettre les réponses d'un quiz pour correction automatique et mise à jour de la progression
- `GET/POST /api/questions/` : Gestion des questions
- `GET/POST /api/answers/` : Gestion des réponses

### 📊 Suivi Apprenant (`/api/activity/progress/`)
- `GET /api/activity/progress/` : Consultation de la progression (Étudiant voit sa progression, Enseignant voit ses élèves, Admin voit tout)
- `POST/PUT /api/activity/progress/` : Enregistrer/Mettre à jour la progression d'un cours

### 🩺 Health Check (`/health/`)
- `GET /health/` : Vérifier l'état de l'API (Retourne HTTP 200 `{"status": "ok", "service": "MadaLearn Backend"}`). Très utile pour le monitoring ou vérifier que Gunicorn/Docker tournent.

---

## 🧪 Tests Automatisés

Pour exécuter la suite de tests automatisés :
```bash
python manage.py test
```
