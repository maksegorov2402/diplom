from django.urls import path

from app.reports.views import EmployeeReportView, LowStockReportView, ReceiptReportView, ReportsIndexView, ShipmentReportView, StockReportView

urlpatterns = [
    path("", ReportsIndexView.as_view(), name="reports-index"),
    path("stocks/", StockReportView.as_view(), name="report-stock"),
    path("receipts/", ReceiptReportView.as_view(), name="report-receipts"),
    path("shipments/", ShipmentReportView.as_view(), name="report-shipments"),
    path("employees/", EmployeeReportView.as_view(), name="report-employees"),
    path("low-stock/", LowStockReportView.as_view(), name="report-low-stock"),
]
