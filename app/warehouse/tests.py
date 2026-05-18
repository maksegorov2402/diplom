from decimal import Decimal

from django.test import TestCase

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
