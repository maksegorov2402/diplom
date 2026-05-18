from django.urls import path

from app.logs.views import OperationLogListView

urlpatterns = [
    path("", OperationLogListView.as_view(), name="operation-log-list"),
]
