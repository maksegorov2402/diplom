from django import forms

from app.config.forms import BootstrapForm, BootstrapModelForm
from app.products.models import Category, Product
from app.warehouse.models import WarehouseLocation


class WarehouseLocationForm(BootstrapModelForm):
    class Meta:
        model = WarehouseLocation
        fields = ["name", "description"]


class StockFilterForm(BootstrapForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label="Товар")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория")
    location = forms.ModelChoiceField(queryset=WarehouseLocation.objects.all(), required=False, label="Зона")
