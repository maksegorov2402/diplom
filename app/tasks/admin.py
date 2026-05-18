from django.contrib import admin

from app.tasks.models import WarehouseTask


@admin.register(WarehouseTask)
class WarehouseTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task_type", "assigned_to", "created_by", "status", "priority", "due_date")
    list_filter = ("task_type", "status", "priority", "due_date")
    search_fields = ("title", "assigned_to__username", "created_by__username")
