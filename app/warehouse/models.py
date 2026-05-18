from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from app.products.models import Product


class WarehouseLocation(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        ordering = ["name"]
        verbose_name = "Складская зона"
        verbose_name_plural = "Складские зоны"

    def __str__(self) -> str:
        return self.name


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks", verbose_name="Товар")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, related_name="stocks", verbose_name="Зона")
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Количество",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        unique_together = ("product", "location")
        ordering = ["product__name", "location__name"]
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self) -> str:
        return f"{self.product} @ {self.location}: {self.quantity}"

    @property
    def below_minimum(self) -> bool:
        return self.quantity < self.product.min_quantity
