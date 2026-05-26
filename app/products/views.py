from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from app.accounts.mixins import MANAGEMENT_ROLES, ModelFormTitleMixin, RoleRequiredMixin
from app.logs.services import log_operation
from app.products.forms import CategoryForm, ProductFilterForm, ProductForm
from app.products.models import Category, Product


class CategoryListCreateView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = MANAGEMENT_ROLES
    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form", CategoryForm())
        return context

    def post(self, request, *args, **kwargs):
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, "Категория создана.")
            log_operation(user=request.user, operation_type="product_created", entity=category, description=f"Создана категория {category.name}")
            return redirect("categories")
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class CategoryUpdateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, UpdateView):
    allowed_roles = MANAGEMENT_ROLES
    model = Category
    form_class = CategoryForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("categories")
    form_title = "редактирование категории"

    def form_valid(self, form):
        messages.success(self.request, "Категория обновлена.")
        return super().form_valid(form)


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = Product.objects.select_related("category")
        self.filter_form = ProductFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data.get("search")
            category = self.filter_form.cleaned_data.get("category")
            if search:
                queryset = queryset.filter(Q(name__icontains=search) | Q(article__icontains=search))
            if category:
                queryset = queryset.filter(category=category)
        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class ProductCreateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, CreateView):
    allowed_roles = MANAGEMENT_ROLES
    model = Product
    form_class = ProductForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("product-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_operation(user=self.request.user, operation_type="product_created", entity=self.object, description=f"Создан товар {self.object}")
        messages.success(self.request, "Товар создан.")
        return response


class ProductUpdateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, UpdateView):
    allowed_roles = MANAGEMENT_ROLES
    model = Product
    form_class = ProductForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("product-list")

    def form_valid(self, form):
        messages.success(self.request, "Товар обновлен.")
        return super().form_valid(form)


class ProductToggleActiveView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = MANAGEMENT_ROLES

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs["pk"])
        product.is_active = not product.is_active
        product.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "Статус товара обновлен.")
        return redirect("product-list")
