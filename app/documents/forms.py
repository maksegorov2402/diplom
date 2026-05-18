from django import forms
from django.forms import formset_factory

from app.config.forms import BootstrapForm, BootstrapModelForm
from app.documents.models import Client, Receipt, Shipment, StockMovement, Supplier, WriteOff
from app.products.models import Product
from app.warehouse.models import WarehouseLocation


class SupplierForm(BootstrapModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "phone", "email", "address"]


class ClientForm(BootstrapModelForm):
    class Meta:
        model = Client
        fields = ["name", "contact_person", "phone", "email", "address"]


class ReceiptForm(BootstrapModelForm):
    receipt_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Дата поступления")

    class Meta:
        model = Receipt
        fields = ["receipt_number", "supplier", "receipt_date", "comment"]


class ShipmentForm(BootstrapModelForm):
    shipment_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Дата отгрузки")

    class Meta:
        model = Shipment
        fields = ["shipment_number", "client", "shipment_date", "status", "comment"]


class ReceiptItemForm(BootstrapForm):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True), label="Товар")
    location = forms.ModelChoiceField(queryset=WarehouseLocation.objects.all(), label="Зона")
    quantity = forms.DecimalField(min_value=0.01, decimal_places=2, label="Количество")
    purchase_price = forms.DecimalField(min_value=0, decimal_places=2, label="Закупочная цена")


class ShipmentItemForm(BootstrapForm):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True), label="Товар")
    location = forms.ModelChoiceField(queryset=WarehouseLocation.objects.all(), label="Зона")
    quantity = forms.DecimalField(min_value=0.01, decimal_places=2, label="Количество")
    sale_price = forms.DecimalField(min_value=0, decimal_places=2, label="Цена продажи")


ReceiptItemFormSet = formset_factory(ReceiptItemForm, extra=3, min_num=1, validate_min=True)
ShipmentItemFormSet = formset_factory(ShipmentItemForm, extra=3, min_num=1, validate_min=True)


class StockMovementForm(BootstrapModelForm):
    movement_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Дата перемещения")

    class Meta:
        model = StockMovement
        fields = ["product", "from_location", "to_location", "quantity", "movement_date", "comment"]


class WriteOffForm(BootstrapModelForm):
    write_off_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Дата списания")

    class Meta:
        model = WriteOff
        fields = ["product", "location", "quantity", "reason", "write_off_date", "comment"]


class ReceiptFilterForm(BootstrapForm):
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False, label="Поставщик")
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата от")
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата до")


class ShipmentFilterForm(BootstrapForm):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, label="Клиент")
    status = forms.ChoiceField(required=False, choices=[("", "Все")] + list(Shipment.STATUS_CHOICES), label="Статус")
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата от")
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Дата до")
