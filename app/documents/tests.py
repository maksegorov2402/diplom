from datetime import date
from decimal import Decimal

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from app.accounts.constants import ROLE_MANAGER
from app.documents.models import Client, Shipment, Supplier, WriteOff
from app.documents.services import StockError, create_receipt, create_shipment, create_write_off
from app.products.models import Category, Product
from app.warehouse.models import Stock, WarehouseLocation


class DocumentServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pass")
        category = Category.objects.create(name="Категория")
        self.product = Product.objects.create(name="Товар", article="ART-1", category=category, unit="шт", price=10, min_quantity=2)
        self.location = WarehouseLocation.objects.create(name="A")
        self.supplier = Supplier.objects.create(name="Поставщик")
        self.client = Client.objects.create(name="Клиент")

    def test_create_receipt_adds_stock(self):
        create_receipt(
            user=self.user,
            receipt_data={"receipt_number": "R-1", "supplier": self.supplier, "receipt_date": date.today(), "comment": ""},
            items_data=[{"product": self.product, "location": self.location, "quantity": Decimal("5"), "purchase_price": Decimal("10")}],
        )
        self.assertEqual(Stock.objects.get(product=self.product, location=self.location).quantity, Decimal("5"))

    def test_create_completed_shipment_reduces_stock(self):
        create_receipt(
            user=self.user,
            receipt_data={"receipt_number": "R-2", "supplier": self.supplier, "receipt_date": date.today(), "comment": ""},
            items_data=[{"product": self.product, "location": self.location, "quantity": Decimal("5"), "purchase_price": Decimal("10")}],
        )
        create_shipment(
            user=self.user,
            shipment_data={"shipment_number": "S-1", "client": self.client, "shipment_date": date.today(), "status": Shipment.STATUS_COMPLETED, "comment": ""},
            items_data=[{"product": self.product, "location": self.location, "quantity": Decimal("2"), "sale_price": Decimal("15")}],
        )
        self.assertEqual(Stock.objects.get(product=self.product, location=self.location).quantity, Decimal("3"))

    def test_write_off_validates_stock_balance(self):
        with self.assertRaises(StockError):
            create_write_off(
                user=self.user,
                write_off_data={"product": self.product, "location": self.location, "quantity": Decimal("1"), "reason": WriteOff.REASON_OTHER, "write_off_date": date.today(), "comment": ""},
            )


class ContactUpdateViewTests(TestCase):
    def setUp(self):
        self.manager_group = Group.objects.create(name=ROLE_MANAGER)
        self.manager = User.objects.create_user(username="manager", password="pass")
        self.manager.groups.add(self.manager_group)
        self.supplier = Supplier.objects.create(name="Поставщик")
        self.client_obj = Client.objects.create(name="Клиент")

    def test_supplier_list_shows_edit_button(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("supplier-list"))
        self.assertContains(response, reverse("supplier-update", args=[self.supplier.pk]))
        self.assertContains(response, "Редактирование")

    def test_client_list_shows_edit_button(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("client-list"))
        self.assertContains(response, reverse("client-update", args=[self.client_obj.pk]))
        self.assertContains(response, "Редактирование")

    def test_manager_can_update_supplier_and_client(self):
        self.client.force_login(self.manager)
        supplier_response = self.client.post(
            reverse("supplier-update", args=[self.supplier.pk]),
            {"name": "Поставщик 2", "contact_person": "", "phone": "", "email": "", "address": ""},
        )
        client_response = self.client.post(
            reverse("client-update", args=[self.client_obj.pk]),
            {"name": "Клиент 2", "contact_person": "", "phone": "", "email": "", "address": ""},
        )
        self.assertRedirects(supplier_response, reverse("supplier-list"))
        self.assertRedirects(client_response, reverse("client-list"))
        self.supplier.refresh_from_db()
        self.client_obj.refresh_from_db()
        self.assertEqual(self.supplier.name, "Поставщик 2")
        self.assertEqual(self.client_obj.name, "Клиент 2")
