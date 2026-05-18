from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView

from app.accounts.constants import ROLE_MANAGER
from app.accounts.mixins import RoleRequiredMixin
from app.warehouse.forms import StockFilterForm, WarehouseLocationForm
from app.warehouse.models import Stock, WarehouseLocation


class WarehouseLocationListCreateView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (ROLE_MANAGER,)
    model = WarehouseLocation
    template_name = "warehouse/location_list.html"
    context_object_name = "locations"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form", WarehouseLocationForm())
        return context

    def post(self, request, *args, **kwargs):
        form = WarehouseLocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Складская зона создана.")
            return redirect("location-list")
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = "warehouse/stock_list.html"
    context_object_name = "stocks"

    def get_queryset(self):
        queryset = Stock.objects.select_related("product", "product__category", "location")
        self.filter_form = StockFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            product = self.filter_form.cleaned_data.get("product")
            category = self.filter_form.cleaned_data.get("category")
            location = self.filter_form.cleaned_data.get("location")
            if product:
                queryset = queryset.filter(product=product)
            if category:
                queryset = queryset.filter(product__category=category)
            if location:
                queryset = queryset.filter(location=location)
        return queryset.order_by("product__name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context
