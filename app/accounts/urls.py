from django.urls import path

from app.accounts.views import StaffListView

urlpatterns = [
    path("staff/", StaffListView.as_view(), name="staff-list"),
]
