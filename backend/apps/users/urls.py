from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    RegisterView,
    UserProfileView,
    CustomTokenObtainPairView,
    UserAdminViewSet,
    RoleViewSet,
    PermissionViewSet,
    ChangePasswordView,
    AvatarUploadView
)

router = DefaultRouter()
router.register(r'admin-users', UserAdminViewSet, basename='admin-user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    path('avatar/', AvatarUploadView.as_view(), name='user-avatar'),
    path('', include(router.urls)),
]
