from django.contrib import admin

from app.products.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "category", "unit", "price", "min_quantity", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "article")
