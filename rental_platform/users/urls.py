from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CreateSupervisorView, CustomTokenObtainPairView, UserProfileView, CreateUserView, CreateAdminView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  # ✅ correct placement

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('register/', CreateUserView.as_view(), name='register'),
    path('admins/create/', CreateAdminView.as_view(), name='create-admin'),
    path('supervisors/', CreateSupervisorView.as_view(), name='create-supervisor'),
]

urlpatterns += router.urls  # ✅ combine path-based and router-based URLs
