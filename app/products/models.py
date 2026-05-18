from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    article = models.CharField(max_length=100, unique=True, verbose_name="Артикул")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория")
    unit = models.CharField(max_length=50, verbose_name="Единица измерения")
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], verbose_name="Цена")
    min_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Минимальный остаток",
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return f"{self.name} ({self.article})"
