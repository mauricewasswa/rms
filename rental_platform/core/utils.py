from .models import AuditLog
from django.utils import timezone
from ipware import get_client_ip

def log_action(user, action, details='', obj=None, request=None):
    ip = None
    if request:
        ip, _ = get_client_ip(request)
    
    AuditLog.objects.create(
        user=user,
        action=action,
        object_type=obj.__class__.__name__ if obj else '',
        object_id=obj.id if obj else '',
        details=details,
        ip_address=ip
    )