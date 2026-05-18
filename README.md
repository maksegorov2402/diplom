# warehouse_system

Веб-приложение для автоматизации складской деятельности: учет товаров, остатков, поступлений, отгрузок, перемещений, списаний, задач сотрудников и отчетности.

## Технологии

- Python 3.12
- Django 5.2
- PostgreSQL
- Docker / Docker Compose
- Bootstrap 5 + Django Templates
- openpyxl
- Gunicorn
- django-environ

## Структура проекта

```text
warehouse_system/
├── app/
│   ├── accounts/
│   ├── products/
│   ├── warehouse/
│   ├── documents/
│   ├── tasks/
│   ├── reports/
│   ├── logs/
│   ├── templates/
│   ├── static/
│   └── config/
├── docker/
│   └── web/
│       ├── Dockerfile
│       └── entrypoint.sh
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── manage.py
└── README.md
```

## Возможности

- авторизация и роли admin / manager / warehouse_worker;
- справочник товаров и категорий;
- складские зоны и остатки;
- поступления, отгрузки, перемещения и списания;
- задачи сотрудников и список «Мои задачи»;
- журнал операций;
- HTML-отчеты и экспорт в Excel.

## Запуск через Docker Compose

1. Скопируйте переменные окружения:

   ```bash
   cp .env.example .env
   ```

2. Запустите приложение:

   ```bash
   docker compose up --build
   ```

3. После запуска приложение доступно по адресу <http://localhost:8000>.

## Миграции

```bash
docker compose exec web python manage.py migrate
```

## Создание суперпользователя

```bash
docker compose exec web python manage.py createsuperuser
```

## Загрузка тестовых данных

```bash
docker compose exec web python manage.py seed_data
```

Будут созданы пользователи:

- `admin` / `admin12345`
- `manager` / `manager12345`
- `worker` / `worker12345`

## Локальный запуск без Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Основные разделы

- `/dashboard/` — дашборд;
- `/products/` — товары и категории;
- `/warehouse/stocks/` — остатки;
- `/documents/` — документы и складские операции;
- `/tasks/` — задачи;
- `/reports/` — отчеты;
- `/logs/` — журнал операций.
