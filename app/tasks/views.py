from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from app.accounts.constants import ROLE_MANAGER
from app.accounts.mixins import ModelFormTitleMixin, RoleRequiredMixin, user_has_role
from app.logs.services import log_operation
from app.tasks.forms import WarehouseTaskForm, WarehouseTaskStatusForm
from app.tasks.models import WarehouseTask


class TaskListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (ROLE_MANAGER,)
    model = WarehouseTask
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return WarehouseTask.objects.select_related("assigned_to", "created_by").order_by("due_date", "-created_at")


class MyTaskListView(LoginRequiredMixin, ListView):
    model = WarehouseTask
    template_name = "tasks/my_tasks.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return WarehouseTask.objects.select_related("assigned_to", "created_by").filter(assigned_to=self.request.user).order_by("due_date", "-created_at")


class TaskCreateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, CreateView):
    allowed_roles = (ROLE_MANAGER,)
    model = WarehouseTask
    form_class = WarehouseTaskForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("task-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_operation(user=self.request.user, operation_type="task_created", entity=self.object, description=f"Создана задача {self.object.title}")
        messages.success(self.request, "Задача создана.")
        return response


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = WarehouseTask
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if task.assigned_to != request.user and not user_has_role(request.user, ROLE_MANAGER):
            return redirect("my-tasks")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_form"] = kwargs.get("status_form", WarehouseTaskStatusForm(initial={"status": self.object.status, "comment": self.object.comment}))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.assigned_to != request.user and not user_has_role(request.user, ROLE_MANAGER):
            return redirect("my-tasks")
        status_form = WarehouseTaskStatusForm(request.POST)
        if status_form.is_valid():
            self.object.status = status_form.cleaned_data["status"]
            self.object.comment = status_form.cleaned_data["comment"]
            self.object.save()
            if self.object.status == WarehouseTask.STATUS_COMPLETED:
                log_operation(user=request.user, operation_type="task_completed", entity=self.object, description=f"Завершена задача {self.object.title}")
            messages.success(request, "Статус задачи обновлен.")
            return redirect("task-detail", pk=self.object.pk)
        return self.render_to_response(self.get_context_data(status_form=status_form))
