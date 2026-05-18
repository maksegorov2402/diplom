from django.contrib import admin

from app.warehouse.models import Stock, WarehouseLocation


@admin.register(WarehouseLocation)
class WarehouseLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "location", "quantity", "updated_at")
    list_filter = ("location", "product__category")
    search_fields = ("product__name", "product__article", "location__name")
