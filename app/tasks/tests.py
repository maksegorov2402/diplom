from datetime import timedelta

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from app.accounts.constants import ROLE_MANAGER
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


class TaskUpdateViewTests(TestCase):
    def setUp(self):
        self.manager_group = Group.objects.create(name=ROLE_MANAGER)
        self.manager = User.objects.create_user(username="manager", password="pass", is_staff=True)
        self.manager.groups.add(self.manager_group)
        self.worker = User.objects.create_user(username="worker", password="pass", is_staff=True)
        self.task = WarehouseTask.objects.create(
            title="Старая задача",
            task_type=WarehouseTask.TYPE_INVENTORY,
            assigned_to=self.worker,
            created_by=self.manager,
            status=WarehouseTask.STATUS_CREATED,
            priority=WarehouseTask.PRIORITY_MEDIUM,
        )

    def test_manager_sees_edit_buttons(self):
        self.client.force_login(self.manager)
        list_response = self.client.get(reverse("task-list"))
        detail_response = self.client.get(reverse("task-detail", args=[self.task.pk]))
        self.assertContains(list_response, reverse("task-update", args=[self.task.pk]))
        self.assertContains(detail_response, reverse("task-update", args=[self.task.pk]))

    def test_manager_can_update_task(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("task-update", args=[self.task.pk]),
            {
                "title": "Новая задача",
                "task_type": WarehouseTask.TYPE_INVENTORY,
                "description": "Обновлено",
                "assigned_to": self.worker.pk,
                "status": WarehouseTask.STATUS_IN_PROGRESS,
                "priority": WarehouseTask.PRIORITY_HIGH,
                "due_date": "",
                "comment": "Комментарий",
            },
        )
        self.assertRedirects(response, reverse("task-list"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Новая задача")

    def test_worker_does_not_see_edit_button(self):
        self.client.force_login(self.worker)
        list_response = self.client.get(reverse("my-tasks"))
        detail_response = self.client.get(reverse("task-detail", args=[self.task.pk]))
        self.assertNotContains(list_response, "Редактирование")
        self.assertNotContains(detail_response, reverse("task-update", args=[self.task.pk]))
