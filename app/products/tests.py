from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from app.accounts.constants import ROLE_MANAGER
from app.documents.models import WriteOff
from app.products.models import Category, Product
from app.warehouse.models import WarehouseLocation


class ProductDeleteViewTests(TestCase):
    def setUp(self):
        self.manager_group = Group.objects.create(name=ROLE_MANAGER)
        self.manager = User.objects.create_user(username="manager", password="pass")
        self.manager.groups.add(self.manager_group)

        self.category = Category.objects.create(name="Категория", description="Описание")
        self.product = Product.objects.create(
            name="Товар",
            article="ART-1",
            category=self.category,
            unit="шт",
            price=Decimal("10.00"),
            min_quantity=Decimal("0"),
            description="Описание",
        )
        self.location = WarehouseLocation.objects.create(name="Зона A", description="Описание")
        self.write_off = WriteOff.objects.create(
            product=self.product,
            location=self.location,
            quantity=Decimal("1.00"),
            reason=WriteOff.REASON_DAMAGE,
            user=self.manager,
            write_off_date="2026-06-07",
            comment="Тест",
        )

    def test_manager_sees_user_friendly_message_when_product_has_related_write_offs(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("product-delete", args=[self.product.pk]),
            follow=True,
        )

        self.assertRedirects(response, reverse("product-list"))
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
        self.assertContains(response, "Невозможно удалить товар")
        self.assertContains(response, "есть связанные списания")


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
