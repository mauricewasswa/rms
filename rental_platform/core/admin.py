from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'object_type', 'object_id', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'details', 'object_id')
    readonly_fields = ('user', 'action', 'object_type', 'object_id', 'details', 'timestamp', 'ip_address')