from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from app.tasks.models import WarehouseTask


class WarehouseTaskModelTests(TestCase):
    def test_completed_task_sets_completion_timestamp(self):
        user = User.objects.create_user(username="worker", password="pass")
        task = WarehouseTask.objects.create(
            title="Проверить зону",
            task_type=WarehouseTask.TYPE_INVENTORY,
            assigned_to=user,
            created_by=user,
            status=WarehouseTask.STATUS_COMPLETED,
            priority=WarehouseTask.PRIORITY_MEDIUM,
        )
        self.assertIsNotNone(task.completed_at)

    def test_overdue_property(self):
        user = User.objects.create_user(username="worker2", password="pass")
        task = WarehouseTask.objects.create(
            title="Проверить отгрузку",
            task_type=WarehouseTask.TYPE_SHIP_GOODS,
            assigned_to=user,
            created_by=user,
            status=WarehouseTask.STATUS_CREATED,
            priority=WarehouseTask.PRIORITY_MEDIUM,
            due_date=timezone.localdate() - timedelta(days=1),
        )
        self.assertTrue(task.is_overdue)
