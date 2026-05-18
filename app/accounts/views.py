from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Count, F, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, RedirectView, TemplateView

from app.accounts.constants import ROLE_MANAGER
from app.accounts.mixins import RoleRequiredMixin
from app.documents.models import Receipt, Shipment
from app.logs.models import OperationLog
from app.products.models import Product
from app.tasks.models import WarehouseTask
from app.warehouse.models import Stock


class WarehouseLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class HomeRedirectView(RedirectView):
    pattern_name = "dashboard"

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse_lazy("dashboard")
        return reverse_lazy("login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        context.update(
            {
                "product_count": Product.objects.filter(is_active=True).count(),
                "low_stock_count": Stock.objects.select_related("product").filter(quantity__lt=F("product__min_quantity")).count(),
                "active_tasks_count": WarehouseTask.objects.exclude(status__in=[WarehouseTask.STATUS_COMPLETED, WarehouseTask.STATUS_CANCELLED]).count(),
                "overdue_tasks_count": WarehouseTask.objects.filter(due_date__lt=today).exclude(status__in=[WarehouseTask.STATUS_COMPLETED, WarehouseTask.STATUS_CANCELLED]).count(),
                "recent_operations": OperationLog.objects.select_related("user")[:10],
                "recent_receipts": Receipt.objects.select_related("supplier", "user")[:5],
                "recent_shipments": Shipment.objects.select_related("client", "user")[:5],
            }
        )
        return context


class StaffListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (ROLE_MANAGER,)
    model = User
    template_name = "accounts/staff_list.html"
    context_object_name = "staff_list"

    def get_queryset(self):
        return (
            User.objects.filter(is_staff=True)
            .annotate(
                operation_count=Count("operation_logs", distinct=True),
                assigned_tasks_count=Count("assigned_tasks", distinct=True),
                completed_tasks_count=Count("assigned_tasks", filter=Q(assigned_tasks__status=WarehouseTask.STATUS_COMPLETED), distinct=True),
            )
            .order_by("username")
        )
