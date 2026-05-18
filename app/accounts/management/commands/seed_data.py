from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from app.accounts.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_WAREHOUSE_WORKER
from app.documents.models import Client, Supplier
from app.products.models import Category, Product
from app.warehouse.models import Stock, WarehouseLocation


class Command(BaseCommand):
    help = "Заполняет систему тестовыми данными."

    def handle(self, *args, **options):
        for role in [ROLE_ADMIN, ROLE_MANAGER, ROLE_WAREHOUSE_WORKER]:
            Group.objects.get_or_create(name=role)

        admin, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True})
        if created:
            admin.set_password("admin12345")
            admin.save()
        admin.groups.add(Group.objects.get(name=ROLE_ADMIN))

        manager, created = User.objects.get_or_create(username="manager", defaults={"email": "manager@example.com", "is_staff": True})
        if created:
            manager.set_password("manager12345")
            manager.save()
        manager.groups.add(Group.objects.get(name=ROLE_MANAGER))

        worker, created = User.objects.get_or_create(username="worker", defaults={"email": "worker@example.com", "is_staff": True})
        if created:
            worker.set_password("worker12345")
            worker.save()
        worker.groups.add(Group.objects.get(name=ROLE_WAREHOUSE_WORKER))

        electronics, _ = Category.objects.get_or_create(name="Электроника")
        packing, _ = Category.objects.get_or_create(name="Упаковка")
        tools, _ = Category.objects.get_or_create(name="Инструменты")

        products = [
            {"name": "Сканер штрихкодов", "article": "SCN-001", "category": electronics, "unit": "шт", "price": Decimal("7500"), "min_quantity": Decimal("3")},
            {"name": "Коробка 40x40", "article": "BOX-040", "category": packing, "unit": "шт", "price": Decimal("35"), "min_quantity": Decimal("50")},
            {"name": "Погрузочный ремень", "article": "RIG-100", "category": tools, "unit": "шт", "price": Decimal("1200"), "min_quantity": Decimal("5")},
        ]
        created_products = []
        for product_data in products:
            product, _ = Product.objects.get_or_create(article=product_data["article"], defaults=product_data)
            created_products.append(product)

        rack_a, _ = WarehouseLocation.objects.get_or_create(name="Стеллаж A", defaults={"description": "Основная зона хранения"})
        rack_b, _ = WarehouseLocation.objects.get_or_create(name="Стеллаж B", defaults={"description": "Резервная зона"})
        loading, _ = WarehouseLocation.objects.get_or_create(name="Зона погрузки", defaults={"description": "Отгрузка"})

        Supplier.objects.get_or_create(name="ООО Поставка", defaults={"contact_person": "Иван Петров", "phone": "+79990000001"})
        Supplier.objects.get_or_create(name="Логистик Снаб", defaults={"contact_person": "Ольга Смирнова", "phone": "+79990000002"})

        Client.objects.get_or_create(name="Торговая сеть А", defaults={"contact_person": "Павел Иванов", "phone": "+79990000003"})
        Client.objects.get_or_create(name="Розница Б", defaults={"contact_person": "Анна Кузнецова", "phone": "+79990000004"})

        initial_stocks = [
            (created_products[0], rack_a, Decimal("10")),
            (created_products[1], rack_b, Decimal("200")),
            (created_products[2], loading, Decimal("4")),
        ]
        for product, location, quantity in initial_stocks:
            Stock.objects.update_or_create(product=product, location=location, defaults={"quantity": quantity})

        self.stdout.write(self.style.SUCCESS("Тестовые данные загружены."))
