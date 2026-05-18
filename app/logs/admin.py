from django.contrib import admin

from app.logs.models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "operation_type", "entity_type", "entity_id")
    list_filter = ("operation_type", "entity_type", "created_at")
    search_fields = ("description", "user__username", "entity_type")
