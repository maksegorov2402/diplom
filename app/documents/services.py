from django.db import transaction

from app.documents.models import Receipt, ReceiptItem, Shipment, ShipmentItem, WriteOff
from app.logs.services import log_operation
from app.warehouse.services import StockError, add_stock, remove_stock


@transaction.atomic
def create_receipt(*, user, receipt_data: dict, items_data: list[dict]) -> Receipt:
    receipt = Receipt.objects.create(user=user, **receipt_data)
    for item in items_data:
        receipt_item = ReceiptItem.objects.create(receipt=receipt, **item)
        add_stock(product=receipt_item.product, location=receipt_item.location, quantity=receipt_item.quantity)
    log_operation(
        user=user,
        operation_type="receipt_created",
        entity=receipt,
        description=f"Создано поступление {receipt.receipt_number}",
    )
    return receipt


@transaction.atomic
def create_shipment(*, user, shipment_data: dict, items_data: list[dict]) -> Shipment:
    shipment = Shipment.objects.create(user=user, **shipment_data)
    for item in items_data:
        shipment_item = ShipmentItem.objects.create(shipment=shipment, **item)
        if shipment.status == Shipment.STATUS_COMPLETED:
            remove_stock(product=shipment_item.product, location=shipment_item.location, quantity=shipment_item.quantity)
    log_operation(
        user=user,
        operation_type="shipment_created",
        entity=shipment,
        description=f"Создана отгрузка {shipment.shipment_number}",
    )
    return shipment


@transaction.atomic
def create_write_off(*, user, write_off_data: dict) -> WriteOff:
    write_off = WriteOff.objects.create(user=user, **write_off_data)
    remove_stock(product=write_off.product, location=write_off.location, quantity=write_off.quantity)
    log_operation(
        user=user,
        operation_type="write_off_created",
        entity=write_off,
        description=f"Создано списание товара {write_off.product}",
    )
    return write_off


__all__ = ["create_receipt", "create_shipment", "create_write_off", "StockError"]
