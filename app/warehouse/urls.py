from django.urls import path

from app.warehouse.views import StockListView, WarehouseLocationListCreateView, WarehouseLocationUpdateView

urlpatterns = [
    path("stocks/", StockListView.as_view(), name="stock-list"),
    path("locations/", WarehouseLocationListCreateView.as_view(), name="location-list"),
    path("locations/<int:pk>/edit/", WarehouseLocationUpdateView.as_view(), name="location-update"),
]
