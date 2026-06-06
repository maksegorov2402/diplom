from django.urls import path

from app.products.views import (
    CategoryListCreateView,
    CategoryUpdateView,
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductToggleActiveView,
    ProductUpdateView,
)

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("create/", ProductCreateView.as_view(), name="product-create"),
    path("<int:pk>/edit/", ProductUpdateView.as_view(), name="product-update"),
    path("<int:pk>/toggle/", ProductToggleActiveView.as_view(), name="product-toggle"),
    path("<int:pk>/delete/", ProductDeleteView.as_view(), name="product-delete"),

    path("categories/", CategoryListCreateView.as_view(), name="categories"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category-update"),
]