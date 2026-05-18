from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from app.products.models import Product
from app.warehouse.models import WarehouseLocation


class ContactBase(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    contact_person = models.CharField(max_length=255, blank=True, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Адрес")

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Supplier(ContactBase):
    class Meta(ContactBase.Meta):
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"


class Client(ContactBase):
    class Meta(ContactBase.Meta):
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Receipt(models.Model):
    receipt_number = models.CharField(max_length=100, unique=True, verbose_name="Номер поступления")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="receipts", verbose_name="Поставщик")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="receipts", verbose_name="Сотрудник")
    receipt_date = models.DateField(verbose_name="Дата поступления")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ["-receipt_date", "-created_at"]
        verbose_name = "Поступление"
        verbose_name_plural = "Поступления"

    def __str__(self) -> str:
        return self.receipt_number


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="items", verbose_name="Поступление")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.PROTECT, verbose_name="Зона")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Количество")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], verbose_name="Закупочная цена")

    class Meta:
        verbose_name = "Позиция поступления"
        verbose_name_plural = "Позиции поступления"

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"


class Shipment(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Черновик"),
        (STATUS_COMPLETED, "Завершена"),
        (STATUS_CANCELLED, "Отменена"),
    ]

    shipment_number = models.CharField(max_length=100, unique=True, verbose_name="Номер отгрузки")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="shipments", verbose_name="Клиент")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shipments", verbose_name="Сотрудник")
    shipment_date = models.DateField(verbose_name="Дата отгрузки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_COMPLETED, verbose_name="Статус")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ["-shipment_date", "-created_at"]
        verbose_name = "Отгрузка"
        verbose_name_plural = "Отгрузки"

    def __str__(self) -> str:
        return self.shipment_number


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="items", verbose_name="Отгрузка")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.PROTECT, verbose_name="Зона")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Количество")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], verbose_name="Цена продажи")

    class Meta:
        verbose_name = "Позиция отгрузки"
        verbose_name_plural = "Позиции отгрузки"

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    from_location = models.ForeignKey(
        WarehouseLocation,
        on_delete=models.PROTECT,
        related_name="outgoing_movements",
        verbose_name="Из зоны",
    )
    to_location = models.ForeignKey(
        WarehouseLocation,
        on_delete=models.PROTECT,
        related_name="incoming_movements",
        verbose_name="В зону",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Количество")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="movements", verbose_name="Сотрудник")
    movement_date = models.DateField(verbose_name="Дата перемещения")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        ordering = ["-movement_date", "-id"]
        verbose_name = "Перемещение"
        verbose_name_plural = "Перемещения"

    def __str__(self) -> str:
        return f"{self.product}: {self.from_location} → {self.to_location}"


class WriteOff(models.Model):
    REASON_DEFECT = "defect"
    REASON_DAMAGE = "damage"
    REASON_EXPIRED = "expired"
    REASON_LOST = "lost"
    REASON_INVENTORY_DIFFERENCE = "inventory_difference"
    REASON_OTHER = "other"
    REASON_CHOICES = [
        (REASON_DEFECT, "Брак"),
        (REASON_DAMAGE, "Повреждение"),
        (REASON_EXPIRED, "Истек срок годности"),
        (REASON_LOST, "Потеря"),
        (REASON_INVENTORY_DIFFERENCE, "Инвентаризационная разница"),
        (REASON_OTHER, "Другое"),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.PROTECT, verbose_name="Зона")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Количество")
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, verbose_name="Причина")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="write_offs", verbose_name="Сотрудник")
    write_off_date = models.DateField(verbose_name="Дата списания")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        ordering = ["-write_off_date", "-id"]
        verbose_name = "Списание"
        verbose_name_plural = "Списания"

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"
