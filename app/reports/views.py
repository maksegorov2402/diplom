from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.generic import TemplateView

from app.accounts.mixins import MANAGEMENT_ROLES, RoleRequiredMixin
from app.documents.models import ReceiptItem, ShipmentItem
from app.logs.services import log_operation
from app.products.models import Product
from app.reports.forms import ReceiptReportFilterForm, ShipmentReportFilterForm, StockReportFilterForm
from app.reports.utils import export_to_excel
from app.tasks.models import WarehouseTask
from app.warehouse.models import Stock


class ReportsIndexView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = MANAGEMENT_ROLES
    template_name = "reports/index.html"


class BaseReportView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = MANAGEMENT_ROLES
    template_name = "reports/report_table.html"
    title = "Отчет"
    filename = "report.xlsx"

    def maybe_export(self, headers, rows):
        if self.request.GET.get("export") == "xlsx":
            log_operation(user=self.request.user, operation_type="report_exported", entity=self, description=f"Экспортирован отчет {self.title}")
            return export_to_excel(filename=self.filename, title=self.title, headers=headers, rows=rows)
        return None

    def render_report(self, *, headers, rows, filter_form):
        export_response = self.maybe_export(headers, rows)
        if export_response:
            return export_response
        return self.render_to_response(self.get_context_data(headers=headers, rows=rows, filter_form=filter_form, title=self.title))


class StockReportView(BaseReportView):
    title = "Отчет по остаткам"
    filename = "stock-report.xlsx"

    def get(self, request, *args, **kwargs):
        filter_form = StockReportFilterForm(request.GET or None)
        queryset = Stock.objects.select_related("product", "product__category", "location")
        if filter_form.is_valid():
            if filter_form.cleaned_data.get("product"):
                queryset = queryset.filter(product=filter_form.cleaned_data["product"])
            if filter_form.cleaned_data.get("category"):
                queryset = queryset.filter(product__category=filter_form.cleaned_data["category"])
            if filter_form.cleaned_data.get("location"):
                queryset = queryset.filter(location=filter_form.cleaned_data["location"])
        headers = ["Товар", "Артикул", "Категория", "Зона", "Количество", "Мин. остаток", "Статус"]
        rows = [[stock.product.name, stock.product.article, stock.product.category.name, stock.location.name, float(stock.quantity), float(stock.product.min_quantity), "Ниже минимума" if stock.below_minimum else "Нормально"] for stock in queryset]
        return self.render_report(headers=headers, rows=rows, filter_form=filter_form)


class ReceiptReportView(BaseReportView):
    title = "Отчет по поступлениям"
    filename = "receipt-report.xlsx"

    def get(self, request, *args, **kwargs):
        filter_form = ReceiptReportFilterForm(request.GET or None)
        queryset = ReceiptItem.objects.select_related("receipt", "receipt__supplier", "receipt__user", "product")
        if filter_form.is_valid():
            if filter_form.cleaned_data.get("date_from"):
                queryset = queryset.filter(receipt__receipt_date__gte=filter_form.cleaned_data["date_from"])
            if filter_form.cleaned_data.get("date_to"):
                queryset = queryset.filter(receipt__receipt_date__lte=filter_form.cleaned_data["date_to"])
            if filter_form.cleaned_data.get("supplier"):
                queryset = queryset.filter(receipt__supplier=filter_form.cleaned_data["supplier"])
            if filter_form.cleaned_data.get("user"):
                queryset = queryset.filter(receipt__user=filter_form.cleaned_data["user"])
        headers = ["Дата", "Номер", "Поставщик", "Товар", "Количество", "Закупочная цена", "Сумма", "Сотрудник"]
        rows = [[str(item.receipt.receipt_date), item.receipt.receipt_number, item.receipt.supplier.name, item.product.name, float(item.quantity), float(item.purchase_price), float(item.quantity * item.purchase_price), item.receipt.user.username] for item in queryset]
        return self.render_report(headers=headers, rows=rows, filter_form=filter_form)


class ShipmentReportView(BaseReportView):
    title = "Отчет по отгрузкам"
    filename = "shipment-report.xlsx"

    def get(self, request, *args, **kwargs):
        filter_form = ShipmentReportFilterForm(request.GET or None)
        queryset = ShipmentItem.objects.select_related("shipment", "shipment__client", "shipment__user", "product")
        if filter_form.is_valid():
            if filter_form.cleaned_data.get("date_from"):
                queryset = queryset.filter(shipment__shipment_date__gte=filter_form.cleaned_data["date_from"])
            if filter_form.cleaned_data.get("date_to"):
                queryset = queryset.filter(shipment__shipment_date__lte=filter_form.cleaned_data["date_to"])
            if filter_form.cleaned_data.get("client"):
                queryset = queryset.filter(shipment__client=filter_form.cleaned_data["client"])
            if filter_form.cleaned_data.get("user"):
                queryset = queryset.filter(shipment__user=filter_form.cleaned_data["user"])
        headers = ["Дата", "Номер", "Клиент", "Товар", "Количество", "Цена продажи", "Сумма", "Сотрудник"]
        rows = [[str(item.shipment.shipment_date), item.shipment.shipment_number, item.shipment.client.name, item.product.name, float(item.quantity), float(item.sale_price), float(item.quantity * item.sale_price), item.shipment.user.username] for item in queryset]
        return self.render_report(headers=headers, rows=rows, filter_form=filter_form)


class EmployeeReportView(BaseReportView):
    title = "Отчет по сотрудникам"
    filename = "employee-report.xlsx"

    def get(self, request, *args, **kwargs):
        today = timezone.localdate()
        users = User.objects.filter(is_staff=True).annotate(
            operation_count=Count("operation_logs", distinct=True),
            assigned_tasks_count=Count("assigned_tasks", distinct=True),
            completed_tasks_count=Count("assigned_tasks", filter=Q(assigned_tasks__status=WarehouseTask.STATUS_COMPLETED), distinct=True),
            overdue_tasks_count=Count(
                "assigned_tasks",
                filter=Q(assigned_tasks__due_date__lt=today) & ~Q(assigned_tasks__status__in=[WarehouseTask.STATUS_COMPLETED, WarehouseTask.STATUS_CANCELLED]),
                distinct=True,
            ),
        )
        headers = ["Сотрудник", "Операции", "Назначено задач", "Выполнено задач", "Просрочено задач", "% выполнения"]
        rows = []
        for user in users:
            completion = round((user.completed_tasks_count / user.assigned_tasks_count) * 100, 2) if user.assigned_tasks_count else 0
            rows.append([user.username, user.operation_count, user.assigned_tasks_count, user.completed_tasks_count, user.overdue_tasks_count, completion])
        return self.render_report(headers=headers, rows=rows, filter_form=None)


class LowStockReportView(BaseReportView):
    title = "Отчет по товарам ниже минимального остатка"
    filename = "low-stock-report.xlsx"

    def get(self, request, *args, **kwargs):
        from django.db.models import DecimalField, Value

        zero_decimal = Value(Decimal("0"), output_field=DecimalField(max_digits=12, decimal_places=2))
        queryset = Product.objects.annotate(total_stock=Coalesce(Sum("stocks__quantity"), zero_decimal)).filter(total_stock__lt=F("min_quantity"))
        headers = ["Товар", "Артикул", "Текущий остаток", "Мин. остаток", "Нужно докупить"]
        rows = [[product.name, product.article, float(product.total_stock), float(product.min_quantity), float(product.min_quantity - product.total_stock)] for product in queryset]
        return self.render_report(headers=headers, rows=rows, filter_form=None)
