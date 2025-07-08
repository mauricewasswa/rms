from rest_framework import viewsets, generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import RentalSite, RentalUnit, Payment
from .serializers import RentalSiteSerializer, RentalUnitSerializer, PaymentSerializer, CreatePaymentSerializer
from users.models import User
from core.models import AuditLog
from core.utils import log_action
from django.shortcuts import get_object_or_404


class RentalSiteViewSet(viewsets.ModelViewSet):
    serializer_class = RentalSiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'address']
    queryset = RentalSite.objects.all()

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'ROOT':
            return RentalSite.objects.all()
        elif user.role == 'ADMIN':
            return user.owned_sites.all()
        elif user.role == 'SUPERVISOR':
            if hasattr(user, 'supervised_site'):
                return RentalSite.objects.filter(id=user.supervised_site.id)
        return RentalSite.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role not in ['ROOT', 'ADMIN']:
            raise permissions.exceptions.PermissionDenied("Only Root or Admin users can create rental sites.")
        
        if self.request.user.role == 'ADMIN':
            serializer.save(admin=self.request.user)
        else:
            serializer.save()
        
        log_action(self.request.user, 'CREATE', f'Created rental site {serializer.instance.name}')

class RentalUnitViewSet(viewsets.ModelViewSet):
    serializer_class = RentalUnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['site', 'status']
    search_fields = ['unit_number', 'description']
    queryset = RentalUnit.objects.all()

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'ROOT':
            return RentalUnit.objects.all()
        elif user.role == 'ADMIN':
            return RentalUnit.objects.filter(site__in=user.owned_sites.all())
        elif user.role == 'SUPERVISOR':
            if hasattr(user, 'supervised_site'):
                return RentalUnit.objects.filter(site=user.supervised_site)
        elif user.role == 'TENANT':
            if hasattr(user, 'rented_unit'):
                return RentalUnit.objects.filter(id=user.rented_unit.id)
        return RentalUnit.objects.none()

    def perform_create(self, serializer):
        site_id = serializer.validated_data['site'].id
        site = get_object_or_404(RentalSite, id=site_id)
        
        if self.request.user.role == 'ADMIN' and site not in self.request.user.owned_sites.all():
            raise permissions.exceptions.PermissionDenied("You can only add units to your own sites.")
        
        serializer.save()
        log_action(self.request.user, 'CREATE', f'Created rental unit {serializer.instance.unit_number}')

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['unit', 'status', 'payment_method']
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePaymentSerializer
        return PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'ROOT':
            return Payment.objects.all()
        elif user.role == 'ADMIN':
            return Payment.objects.filter(unit__site__in=user.owned_sites.all())
        elif user.role == 'SUPERVISOR':
            if hasattr(user, 'supervised_site'):
                return Payment.objects.filter(unit__site=user.supervised_site)
        elif user.role == 'TENANT':
            return user.payments.all()
        return Payment.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'TENANT':
            raise permissions.exceptions.PermissionDenied("Only tenants can make payments.")
        
        unit = serializer.validated_data['unit']
        if not hasattr(self.request.user, 'rented_unit') or self.request.user.rented_unit != unit:
            raise permissions.exceptions.PermissionDenied("You can only pay for your rented unit.")
        
        serializer.save(tenant=self.request.user)
        log_action(self.request.user, 'CREATE', f'Created payment for unit {unit.unit_number}')

class AssignSupervisorView(generics.UpdateAPIView):
    queryset = RentalSite.objects.all()
    serializer_class = RentalSiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.role not in ['ROOT', 'ADMIN']:
            raise permissions.exceptions.PermissionDenied("Only Root or Admin users can assign supervisors.")
        
        site = self.get_object()
        if self.request.user.role == 'ADMIN' and site not in self.request.user.owned_sites.all():
            raise permissions.exceptions.PermissionDenied("You can only assign supervisors to your own sites.")
        
        supervisor_id = self.request.data.get('supervisor_id')
        if not supervisor_id:
            raise serializers.ValidationError("supervisor_id is required.")
        
        supervisor = get_object_or_404(User, id=supervisor_id, role='SUPERVISOR')
        
        # Remove from any previous site
        if hasattr(supervisor, 'supervised_site'):
            old_site = supervisor.supervised_site
            old_site.supervisor = None
            old_site.save()
        
        serializer.instance.supervisor = supervisor
        serializer.save()
        
        log_action(self.request.user, 'UPDATE', f'Assigned supervisor {supervisor.username} to site {serializer.instance.name}')