from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from app.accounts.constants import ROLE_MANAGER
from app.products.models import Category, Product
from app.warehouse.models import Stock, WarehouseLocation
from app.warehouse.services import StockError, add_stock, move_stock, remove_stock


class StockServiceTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Категория")
        self.product = Product.objects.create(name="Товар", article="A-1", category=category, unit="шт", price=10, min_quantity=2)
        self.loc_a = WarehouseLocation.objects.create(name="A")
        self.loc_b = WarehouseLocation.objects.create(name="B")

    def test_add_and_remove_stock(self):
        add_stock(product=self.product, location=self.loc_a, quantity=Decimal("5"))
        remove_stock(product=self.product, location=self.loc_a, quantity=Decimal("2"))
        self.assertEqual(Stock.objects.get(product=self.product, location=self.loc_a).quantity, Decimal("3"))

    def test_cannot_remove_more_than_available(self):
        add_stock(product=self.product, location=self.loc_a, quantity=Decimal("1"))
        with self.assertRaises(StockError):
            remove_stock(product=self.product, location=self.loc_a, quantity=Decimal("2"))

    def test_move_stock(self):
        add_stock(product=self.product, location=self.loc_a, quantity=Decimal("4"))
        move_stock(product=self.product, from_location=self.loc_a, to_location=self.loc_b, quantity=Decimal("1"))
        self.assertEqual(Stock.objects.get(product=self.product, location=self.loc_a).quantity, Decimal("3"))
        self.assertEqual(Stock.objects.get(product=self.product, location=self.loc_b).quantity, Decimal("1"))


class WarehouseLocationUpdateViewTests(TestCase):
    def setUp(self):
        self.manager_group = Group.objects.create(name=ROLE_MANAGER)
        self.manager = User.objects.create_user(username="manager", password="pass")
        self.manager.groups.add(self.manager_group)
        self.location = WarehouseLocation.objects.create(name="A", description="Старая")

    def test_location_list_shows_edit_button(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("location-list"))
        self.assertContains(response, reverse("location-update", args=[self.location.pk]))
        self.assertContains(response, "Редактирование")

    def test_manager_can_update_location(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("location-update", args=[self.location.pk]),
            {"name": "B", "description": "Новая"},
        )
        self.assertRedirects(response, reverse("location-list"))
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, "B")
