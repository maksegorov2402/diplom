from decimal import Decimal

from django.db import transaction
from django.db.models import F

from app.warehouse.models import Stock


class StockError(ValueError):
    pass


def _normalize_quantity(quantity) -> Decimal:
    quantity = Decimal(str(quantity))
    if quantity <= 0:
        raise StockError("Количество должно быть больше 0.")
    return quantity


@transaction.atomic
def add_stock(*, product, location, quantity) -> Stock:
    quantity = _normalize_quantity(quantity)
    stock, _ = Stock.objects.select_for_update().get_or_create(product=product, location=location, defaults={"quantity": 0})
    stock.quantity = F("quantity") + quantity
    stock.save(update_fields=["quantity", "updated_at"])
    stock.refresh_from_db()
    return stock


@transaction.atomic
def remove_stock(*, product, location, quantity) -> Stock:
    quantity = _normalize_quantity(quantity)
    stock, _ = Stock.objects.select_for_update().get_or_create(product=product, location=location, defaults={"quantity": 0})
    stock.refresh_from_db()
    if stock.quantity < quantity:
        raise StockError("Недостаточно товара на складе для выполнения операции.")
    stock.quantity = F("quantity") - quantity
    stock.save(update_fields=["quantity", "updated_at"])
    stock.refresh_from_db()
    return stock


@transaction.atomic
def move_stock(*, product, from_location, to_location, quantity):
    if from_location == to_location:
        raise StockError("Зоны перемещения должны различаться.")
    remove_stock(product=product, location=from_location, quantity=quantity)
    return add_stock(product=product, location=to_location, quantity=quantity)
