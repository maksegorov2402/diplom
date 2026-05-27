from django.urls import path

from app.documents.views import (
    ClientUpdateView,
    ClientListCreateView,
    MovementCreateView,
    MovementListView,
    ReceiptCreateView,
    ReceiptDetailView,
    ReceiptListView,
    ShipmentCreateView,
    ShipmentDetailView,
    ShipmentListView,
    SupplierUpdateView,
    SupplierListCreateView,
    WriteOffCreateView,
    WriteOffListView,
)

urlpatterns = [
    path("suppliers/", SupplierListCreateView.as_view(), name="supplier-list"),
    path("suppliers/<int:pk>/edit/", SupplierUpdateView.as_view(), name="supplier-update"),
    path("clients/", ClientListCreateView.as_view(), name="client-list"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="client-update"),
    path("receipts/", ReceiptListView.as_view(), name="receipt-list"),
    path("receipts/create/", ReceiptCreateView.as_view(), name="receipt-create"),
    path("receipts/<int:pk>/", ReceiptDetailView.as_view(), name="receipt-detail"),
    path("shipments/", ShipmentListView.as_view(), name="shipment-list"),
    path("shipments/create/", ShipmentCreateView.as_view(), name="shipment-create"),
    path("shipments/<int:pk>/", ShipmentDetailView.as_view(), name="shipment-detail"),
    path("movements/", MovementListView.as_view(), name="movement-list"),
    path("movements/create/", MovementCreateView.as_view(), name="movement-create"),
    path("write-offs/", WriteOffListView.as_view(), name="writeoff-list"),
    path("write-offs/create/", WriteOffCreateView.as_view(), name="writeoff-create"),
]
