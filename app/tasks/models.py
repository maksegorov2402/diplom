from django.conf import settings
from django.db import models
from django.utils import timezone


class WarehouseTask(models.Model):
    TYPE_RECEIVE_GOODS = "receive_goods"
    TYPE_PLACE_GOODS = "place_goods"
    TYPE_COLLECT_ORDER = "collect_order"
    TYPE_SHIP_GOODS = "ship_goods"
    TYPE_MOVE_GOODS = "move_goods"
    TYPE_INVENTORY = "inventory"
    TYPE_WRITE_OFF = "write_off"
    TASK_TYPE_CHOICES = [
        (TYPE_RECEIVE_GOODS, "Принять товар"),
        (TYPE_PLACE_GOODS, "Разместить товар"),
        (TYPE_COLLECT_ORDER, "Собрать заказ"),
        (TYPE_SHIP_GOODS, "Отгрузить товар"),
        (TYPE_MOVE_GOODS, "Переместить товар"),
        (TYPE_INVENTORY, "Инвентаризация"),
        (TYPE_WRITE_OFF, "Списание"),
    ]

    STATUS_CREATED = "created"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_OVERDUE = "overdue"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_IN_PROGRESS, "В работе"),
        (STATUS_COMPLETED, "Завершена"),
        (STATUS_CANCELLED, "Отменена"),
        (STATUS_OVERDUE, "Просрочена"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Низкий"),
        (PRIORITY_MEDIUM, "Средний"),
        (PRIORITY_HIGH, "Высокий"),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, verbose_name="Тип задачи")
    description = models.TextField(blank=True, verbose_name="Описание")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assigned_tasks", verbose_name="Исполнитель")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_tasks", verbose_name="Создал")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED, verbose_name="Статус")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM, verbose_name="Приоритет")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    due_date = models.DateField(null=True, blank=True, verbose_name="Срок")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Завершено")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        ordering = ["status", "due_date", "-created_at"]
        verbose_name = "Складская задача"
        verbose_name_plural = "Складские задачи"

    def __str__(self) -> str:
        return self.title

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_date and self.status not in {self.STATUS_COMPLETED, self.STATUS_CANCELLED} and self.due_date < timezone.localdate())

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.STATUS_COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)
