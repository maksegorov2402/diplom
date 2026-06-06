from django import forms

from app.config.forms import BootstrapForm, BootstrapModelForm
from app.products.models import Category, Product
from app.warehouse.models import WarehouseLocation


class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class ProductForm(BootstrapModelForm):
    location = forms.ModelChoiceField(
        queryset=WarehouseLocation.objects.all(),
        label="Зона",
        required=False
    )

    quantity = forms.DecimalField(
        label="Количество",
        min_value=0,        
        required=False
    )

    class Meta:
        model = Product
        fields = ["name", "article", "category", "unit", "price", "min_quantity", "description", "is_active", "location", "quantity"]


class ProductFilterForm(BootstrapForm):
    search = forms.CharField(required=False, label="Поиск")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория")
