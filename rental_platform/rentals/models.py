from django.db import models
from users.models import User

class RentalSite(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_sites')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class RentalUnit(models.Model):
    UNIT_STATUS = (
        ('VACANT', 'Vacant'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
    )
    
    site = models.ForeignKey(RentalSite, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=UNIT_STATUS, default='VACANT')
    features = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.site.name} - Unit {self.unit_number}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('MPESA', 'M-Pesa'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Credit/Debit Card'),
    )
    
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.amount} by {self.tenant}"