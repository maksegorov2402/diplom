from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from app.accounts.views import DashboardView, HomeRedirectView, WarehouseLoginView

urlpatterns = [
    path("", HomeRedirectView.as_view(), name="home"),
    path("login/", WarehouseLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("admin/", admin.site.urls),
    path("products/", include("app.products.urls")),
    path("warehouse/", include("app.warehouse.urls")),
    path("documents/", include("app.documents.urls")),
    path("tasks/", include("app.tasks.urls")),
    path("reports/", include("app.reports.urls")),
    path("accounts/", include("app.accounts.urls")),
    path("logs/", include("app.logs.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
