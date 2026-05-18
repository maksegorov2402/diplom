from django import forms

from app.config.forms import BootstrapForm, BootstrapModelForm
from app.products.models import Category, Product


class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = ["name", "article", "category", "unit", "price", "min_quantity", "description", "is_active"]


class ProductFilterForm(BootstrapForm):
    search = forms.CharField(required=False, label="Поиск")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория")
