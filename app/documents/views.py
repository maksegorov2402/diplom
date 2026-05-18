from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from app.accounts.constants import ROLE_MANAGER, ROLE_WAREHOUSE_WORKER
from app.accounts.mixins import ModelFormTitleMixin, RoleRequiredMixin
from app.documents.forms import (
    ClientForm,
    ReceiptFilterForm,
    ReceiptForm,
    ReceiptItemFormSet,
    ShipmentFilterForm,
    ShipmentForm,
    ShipmentItemFormSet,
    StockMovementForm,
    SupplierForm,
    WriteOffForm,
)
from app.documents.models import Client, Receipt, Shipment, StockMovement, Supplier, WriteOff
from app.documents.services import StockError, create_receipt, create_shipment, create_write_off
from app.logs.services import log_operation
from app.warehouse.services import move_stock


class SupplierListCreateView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (ROLE_MANAGER,)
    model = Supplier
    template_name = "documents/supplier_list.html"
    context_object_name = "suppliers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form", SupplierForm())
        return context

    def post(self, request, *args, **kwargs):
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Поставщик создан.")
            return redirect("supplier-list")
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class ClientListCreateView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (ROLE_MANAGER,)
    model = Client
    template_name = "documents/client_list.html"
    context_object_name = "clients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form", ClientForm())
        return context

    def post(self, request, *args, **kwargs):
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Клиент создан.")
            return redirect("client-list")
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class ReceiptListView(LoginRequiredMixin, ListView):
    model = Receipt
    template_name = "documents/receipt_list.html"
    context_object_name = "receipts"

    def get_queryset(self):
        queryset = Receipt.objects.select_related("supplier", "user")
        self.filter_form = ReceiptFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            supplier = self.filter_form.cleaned_data.get("supplier")
            date_from = self.filter_form.cleaned_data.get("date_from")
            date_to = self.filter_form.cleaned_data.get("date_to")
            if supplier:
                queryset = queryset.filter(supplier=supplier)
            if date_from:
                queryset = queryset.filter(receipt_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(receipt_date__lte=date_to)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class ReceiptDetailView(LoginRequiredMixin, DetailView):
    model = Receipt
    template_name = "documents/receipt_detail.html"
    context_object_name = "receipt"


class ReceiptCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = (ROLE_MANAGER, ROLE_WAREHOUSE_WORKER)
    model = Receipt
    form_class = ReceiptForm
    template_name = "documents/receipt_form.html"
    success_url = reverse_lazy("receipt-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item_formset"] = kwargs.get("item_formset", ReceiptItemFormSet())
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        item_formset = ReceiptItemFormSet(request.POST)
        if form.is_valid() and item_formset.is_valid():
            items = [item for item in item_formset.cleaned_data if item]
            if items:
                receipt = create_receipt(user=request.user, receipt_data=form.cleaned_data, items_data=items)
                messages.success(request, f"Поступление {receipt.receipt_number} создано.")
                return redirect("receipt-detail", pk=receipt.pk)
            form.add_error(None, "Добавьте хотя бы одну позицию.")
        return render(request, self.template_name, self.get_context_data(form=form, item_formset=item_formset))


class ShipmentListView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = "documents/shipment_list.html"
    context_object_name = "shipments"

    def get_queryset(self):
        queryset = Shipment.objects.select_related("client", "user")
        self.filter_form = ShipmentFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            client = self.filter_form.cleaned_data.get("client")
            status = self.filter_form.cleaned_data.get("status")
            date_from = self.filter_form.cleaned_data.get("date_from")
            date_to = self.filter_form.cleaned_data.get("date_to")
            if client:
                queryset = queryset.filter(client=client)
            if status:
                queryset = queryset.filter(status=status)
            if date_from:
                queryset = queryset.filter(shipment_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(shipment_date__lte=date_to)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class ShipmentDetailView(LoginRequiredMixin, DetailView):
    model = Shipment
    template_name = "documents/shipment_detail.html"
    context_object_name = "shipment"


class ShipmentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = (ROLE_MANAGER, ROLE_WAREHOUSE_WORKER)
    model = Shipment
    form_class = ShipmentForm
    template_name = "documents/shipment_form.html"
    success_url = reverse_lazy("shipment-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item_formset"] = kwargs.get("item_formset", ShipmentItemFormSet())
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        item_formset = ShipmentItemFormSet(request.POST)
        if form.is_valid() and item_formset.is_valid():
            items = [item for item in item_formset.cleaned_data if item]
            if not items:
                form.add_error(None, "Добавьте хотя бы одну позицию.")
            else:
                try:
                    shipment = create_shipment(user=request.user, shipment_data=form.cleaned_data, items_data=items)
                except StockError as exc:
                    form.add_error(None, str(exc))
                else:
                    messages.success(request, f"Отгрузка {shipment.shipment_number} создана.")
                    return redirect("shipment-detail", pk=shipment.pk)
        return render(request, self.template_name, self.get_context_data(form=form, item_formset=item_formset))


class MovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = "documents/movement_list.html"
    context_object_name = "movements"

    def get_queryset(self):
        return StockMovement.objects.select_related("product", "from_location", "to_location", "user")


class MovementCreateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, CreateView):
    allowed_roles = (ROLE_MANAGER, ROLE_WAREHOUSE_WORKER)
    model = StockMovement
    form_class = StockMovementForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("movement-list")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        try:
            with transaction.atomic():
                self.object.save()
                move_stock(product=self.object.product, from_location=self.object.from_location, to_location=self.object.to_location, quantity=self.object.quantity)
                log_operation(user=self.request.user, operation_type="stock_moved", entity=self.object, description=f"Перемещен товар {self.object.product}")
        except StockError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Перемещение создано.")
        return redirect(self.success_url)


class WriteOffListView(LoginRequiredMixin, ListView):
    model = WriteOff
    template_name = "documents/writeoff_list.html"
    context_object_name = "write_offs"

    def get_queryset(self):
        return WriteOff.objects.select_related("product", "location", "user")


class WriteOffCreateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, CreateView):
    allowed_roles = (ROLE_MANAGER, ROLE_WAREHOUSE_WORKER)
    model = WriteOff
    form_class = WriteOffForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("writeoff-list")

    def form_valid(self, form):
        try:
            create_write_off(user=self.request.user, write_off_data=form.cleaned_data)
        except StockError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Списание создано.")
        return redirect(self.success_url)
