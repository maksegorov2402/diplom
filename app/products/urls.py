from django.urls import path

from app.products.views import CategoryListCreateView, ProductCreateView, ProductListView, ProductToggleActiveView, ProductUpdateView

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("create/", ProductCreateView.as_view(), name="product-create"),
    path("<int:pk>/edit/", ProductUpdateView.as_view(), name="product-update"),
    path("<int:pk>/toggle/", ProductToggleActiveView.as_view(), name="product-toggle"),
    path("categories/", CategoryListCreateView.as_view(), name="categories"),
]
