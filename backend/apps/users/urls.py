from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    RegisterView,
    UserProfileView,
    CustomTokenObtainPairView,
    UserListView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('', UserListView.as_view(), name='user-list'),
]
