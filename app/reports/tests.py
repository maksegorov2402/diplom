from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from app.accounts.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_WAREHOUSE_WORKER


class ReportsAccessTests(TestCase):
    def setUp(self):
        self.admin_group = Group.objects.create(name=ROLE_ADMIN)
        self.manager_group = Group.objects.create(name=ROLE_MANAGER)
        self.worker_group = Group.objects.create(name=ROLE_WAREHOUSE_WORKER)

        self.admin = User.objects.create_user(username="admin_role", password="pass", is_staff=True)
        self.admin.groups.add(self.admin_group)

        self.manager = User.objects.create_user(username="manager", password="pass", is_staff=True)
        self.manager.groups.add(self.manager_group)

        self.worker = User.objects.create_user(username="worker", password="pass", is_staff=True)
        self.worker.groups.add(self.worker_group)

    def test_admin_and_manager_can_open_reports(self):
        for user in (self.admin, self.manager):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("reports-index"))
                self.assertEqual(response.status_code, 200)

    def test_worker_cannot_open_reports(self):
        self.client.force_login(self.worker)
        response = self.client.get(reverse("reports-index"))
        self.assertEqual(response.status_code, 403)
