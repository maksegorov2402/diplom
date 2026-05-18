from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from app.accounts.constants import ROLE_MANAGER
from app.accounts.mixins import RoleRequiredMixin
from app.logs.models import OperationLog


class OperationLogListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (ROLE_MANAGER,)
    model = OperationLog
    template_name = "logs/operation_log_list.html"
    context_object_name = "logs"
    paginate_by = 50
