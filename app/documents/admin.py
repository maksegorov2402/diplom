from django.contrib import admin

from app.documents.models import Client, Receipt, ReceiptItem, Shipment, ShipmentItem, StockMovement, Supplier, WriteOff


class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    extra = 0


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "supplier", "user", "receipt_date", "created_at")
    list_filter = ("supplier", "receipt_date")
    search_fields = ("receipt_number", "supplier__name", "user__username")
    inlines = [ReceiptItemInline]


class ShipmentItemInline(admin.TabularInline):
    model = ShipmentItem
    extra = 0


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("shipment_number", "client", "user", "shipment_date", "status")
    list_filter = ("client", "shipment_date", "status")
    search_fields = ("shipment_number", "client__name", "user__username")
    inlines = [ShipmentItemInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email")
    search_fields = ("name", "contact_person", "phone")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email")
    search_fields = ("name", "contact_person", "phone")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "from_location", "to_location", "quantity", "user", "movement_date")
    list_filter = ("movement_date", "from_location", "to_location")
    search_fields = ("product__name", "product__article", "user__username")


@admin.register(WriteOff)
class WriteOffAdmin(admin.ModelAdmin):
    list_display = ("product", "location", "quantity", "reason", "user", "write_off_date")
    list_filter = ("reason", "location", "write_off_date")
    search_fields = ("product__name", "product__article", "user__username")


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ("receipt", "product", "location", "quantity", "purchase_price")


@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ("shipment", "product", "location", "quantity", "sale_price")
