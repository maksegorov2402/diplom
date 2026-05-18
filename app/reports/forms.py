from django import forms
from django.contrib.auth.models import User

from app.config.forms import BootstrapForm
from app.documents.models import Client, Supplier
from app.products.models import Category, Product
from app.warehouse.models import WarehouseLocation


class StockReportFilterForm(BootstrapForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label="Товар")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория")
    location = forms.ModelChoiceField(queryset=WarehouseLocation.objects.all(), required=False, label="Зона")


class ReceiptReportFilterForm(BootstrapForm):
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата от")
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата до")
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False, label="Поставщик")
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), required=False, label="Сотрудник")


class ShipmentReportFilterForm(BootstrapForm):
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата от")
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата до")
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, label="Клиент")
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), required=False, label="Сотрудник")
