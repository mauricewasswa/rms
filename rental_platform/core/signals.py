from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rentals.models import RentalSite, RentalUnit, Payment
from core.utils import log_action

User = get_user_model()

@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    log_action(None, action, f'User {instance.username} {action.lower()}d', instance)

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    log_action(None, 'DELETE', f'User {instance.username} deleted', instance)

@receiver(post_save, sender=RentalSite)
def log_rentalsite_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    log_action(None, action, f'RentalSite {instance.name} {action.lower()}d', instance)

@receiver(post_delete, sender=RentalSite)
def log_rentalsite_delete(sender, instance, **kwargs):
    log_action(None, 'DELETE', f'RentalSite {instance.name} deleted', instance)

# Similar signals for RentalUnit and Payment