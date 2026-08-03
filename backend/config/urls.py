from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),

    # Endpoints API REST
    path('api/users/', include('users.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/books/', include('library.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('quizzes.urls')),
    path('api/', include('activity.urls')),
    path('api/notifications/', include('notifications.urls')),

    # Documentation API (Swagger / OpenAPI 3)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health check
    path('health/', lambda request: __import__('django.http').http.JsonResponse({"status": "ok", "service": "MadaLearn Backend"}), name='health'),
]

# Serving Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
