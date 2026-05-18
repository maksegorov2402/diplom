from django import forms
from django.contrib.auth.models import User

from app.config.forms import BootstrapForm, BootstrapModelForm
from app.tasks.models import WarehouseTask


class WarehouseTaskForm(BootstrapModelForm):
    due_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Срок")

    class Meta:
        model = WarehouseTask
        fields = ["title", "task_type", "description", "assigned_to", "status", "priority", "due_date", "comment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(is_staff=True)


class WarehouseTaskStatusForm(BootstrapForm):
    status = forms.ChoiceField(choices=WarehouseTask.STATUS_CHOICES, label="Статус")
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), label="Комментарий")
