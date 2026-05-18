from django.urls import path

from app.tasks.views import MyTaskListView, TaskCreateView, TaskDetailView, TaskListView

urlpatterns = [
    path("", TaskListView.as_view(), name="task-list"),
    path("create/", TaskCreateView.as_view(), name="task-create"),
    path("my/", MyTaskListView.as_view(), name="my-tasks"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
]
