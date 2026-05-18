#!/bin/sh
set -e

until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn app.config.wsgi:application --bind 0.0.0.0:8000
