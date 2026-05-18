from django.conf import settings
from django.db import models


class OperationLog(models.Model):
    OPERATION_CHOICES = [
        ("product_created", "Создание товара"),
        ("receipt_created", "Поступление"),
        ("shipment_created", "Отгрузка"),
        ("stock_moved", "Перемещение"),
        ("write_off_created", "Списание"),
        ("task_created", "Создание задачи"),
        ("task_completed", "Выполнение задачи"),
        ("report_exported", "Экспорт отчета"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operation_logs",
        verbose_name="Пользователь",
    )
    operation_type = models.CharField(max_length=50, choices=OPERATION_CHOICES, verbose_name="Тип операции")
    entity_type = models.CharField(max_length=100, verbose_name="Сущность")
    entity_id = models.PositiveBigIntegerField(verbose_name="ID сущности")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Журнал операций"
        verbose_name_plural = "Журнал операций"

    def __str__(self) -> str:
        return f"{self.get_operation_type_display()} — {self.entity_type} #{self.entity_id}"
