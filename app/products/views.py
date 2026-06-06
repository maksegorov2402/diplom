from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from app.accounts.mixins import MANAGEMENT_ROLES, ModelFormTitleMixin, RoleRequiredMixin
from app.logs.services import log_operation
from app.products.forms import CategoryForm, ProductFilterForm, ProductForm
from app.products.models import Category, Product
from app.warehouse.models import Stock


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


from django.db.models import Q, Sum

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = (
            Product.objects
            .select_related("category")
            .prefetch_related("stocks")
            .annotate(total_quantity=Sum("stocks__quantity"))
        )

        self.filter_form = ProductFilterForm(self.request.GET or None)

        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data.get("search")
            category = self.filter_form.cleaned_data.get("category")

            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(article__icontains=search)
                )

            if category:
                queryset = queryset.filter(category=category)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", ProductFilterForm())
        return context


class ProductCreateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, CreateView):
    allowed_roles = MANAGEMENT_ROLES
    model = Product
    form_class = ProductForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("product-list")

    def form_valid(self, form):             
        response = super().form_valid(form)

        location = form.cleaned_data.get("location")
        quantity = form.cleaned_data.get("quantity")

        if location:
            Stock.objects.create(
                product=self.object,
                location=location,
                quantity=quantity or 0,
            )

        log_operation(
            user=self.request.user,
            operation_type="product_created",
            entity=self.object,
            description=f"Создан товар {self.object}"
        )

        messages.success(self.request, "Товар создан.")
        return response


class ProductUpdateView(LoginRequiredMixin, RoleRequiredMixin, ModelFormTitleMixin, UpdateView):
    allowed_roles = MANAGEMENT_ROLES
    model = Product
    form_class = ProductForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("product-list")

    def get_initial(self):
        initial = super().get_initial()

        stock = self.object.stocks.first()

        if stock:
            initial["location"] = stock.location
            initial["quantity"] = stock.quantity

        return initial

    def form_valid(self, form):
        response = super().form_valid(form)

        location = form.cleaned_data.get("location")
        quantity = form.cleaned_data.get("quantity")

        if location:
            stock, created = Stock.objects.get_or_create(
                product=self.object,
                location=location,
                defaults={"quantity": quantity or 0},
            )

            if not created:
                stock.quantity = quantity or 0
                stock.save()

        messages.success(self.request, "Товар обновлен.")
        return response

class ProductToggleActiveView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = MANAGEMENT_ROLES

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs["pk"])
        product.is_active = not product.is_active
        product.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "Статус товара обновлен.")
        return redirect("product-list")
    
class ProductDeleteView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = MANAGEMENT_ROLES

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs["pk"])

        try:
            product.delete()
        except ProtectedError:
            messages.error(
                request,
                "Невозможно удалить товар, потому что есть связанные списания. Сначала удалите или измените связанные записи.",
            )
            return redirect("product-list")

        log_operation(user=request.user, operation_type="product_deleted", entity=product, description=f"Удален товар {product}")
        messages.success(request, "Товар удален.")
        return redirect("product-list")
