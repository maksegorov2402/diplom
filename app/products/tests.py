from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from app.accounts.constants import ROLE_MANAGER
from app.products.models import Category


class CategoryUpdateViewTests(TestCase):
    def setUp(self):
        self.manager_group = Group.objects.create(name=ROLE_MANAGER)
        self.manager = User.objects.create_user(username="manager", password="pass")
        self.manager.groups.add(self.manager_group)
        self.category = Category.objects.create(name="Старое имя", description="Описание")

    def test_category_list_shows_edit_button(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("categories"))
        self.assertContains(response, reverse("category-update", args=[self.category.pk]))
        self.assertContains(response, "Редактирование")

    def test_manager_can_update_category(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("category-update", args=[self.category.pk]),
            {"name": "Новое имя", "description": "Новое описание"},
        )
        self.assertRedirects(response, reverse("categories"))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Новое имя")
