from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer, CreateUserSerializer, AdminCreateSerializer, CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rentals.models import RentalSite
from core.models import AuditLog
from core.utils import log_action
from rest_framework import viewsets
from django.db.models import Q


User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAdminUser]

class CreateAdminView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role != 'ROOT':
            return Response({'detail': 'Only Root users can create Admins.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        log_action(request.user, 'CREATE', f'Created admin user {user.username}')
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ROOT':
            return User.objects.all()
        elif user.role == 'ADMIN':
            # Admins see other admins/supervisors/tenants in their sites
            return User.objects.filter(
                Q(managed_sites__in=user.owned_sites.all()) |
                Q(supervised_site__in=user.owned_sites.all()) |
                Q(rented_unit__site__in=user.owned_sites.all())
            ).distinct()
        elif user.role == 'SUPERVISOR':
            # Supervisors see tenants in their site
            return User.objects.filter(
                rented_unit__site=user.supervised_site
            )
        else:  # TENANT
            return User.objects.filter(id=user.id)
        

class CreateSupervisorView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Only allow ADMIN users to create supervisors
        if request.user.role != 'ADMIN':
            return Response(
                {'detail': 'Only admin users can create supervisors.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Force supervisor role
        modified_data = request.data.copy()
        modified_data['role'] = 'SUPERVISOR'
        
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)