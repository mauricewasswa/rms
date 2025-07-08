from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ROOT', 'Root'),
        ('ADMIN', 'Admin'),
        ('SUPERVISOR', 'Supervisor'),
        ('TENANT', 'Tenant'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    
    # Additional fields for different roles
    managed_sites = models.ManyToManyField('rentals.RentalSite', blank=True, related_name='admins')
    supervised_site = models.OneToOneField('rentals.RentalSite', null=True, blank=True, on_delete=models.SET_NULL, related_name='supervisor')
    rented_unit = models.OneToOneField('rentals.RentalUnit', null=True, blank=True, on_delete=models.SET_NULL, related_name='tenant')

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"