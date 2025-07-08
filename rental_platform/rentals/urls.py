from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RentalSiteViewSet, RentalUnitViewSet, PaymentViewSet, AssignSupervisorView

router = DefaultRouter()
router.register(r'sites', RentalSiteViewSet, basename='rentalsite')
router.register(r'units', RentalUnitViewSet, basename='rentalunit')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('sites/<int:pk>/assign-supervisor/', AssignSupervisorView.as_view(), name='assign-supervisor'),
] + router.urls