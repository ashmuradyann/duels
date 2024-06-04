#!/bin/bash

# Создаем миграции
echo "Making migrations..."
python manage.py makemigrations

# Применяем миграции
echo "Applying migrations..."
python manage.py migrate

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Запускаем Django приложение через uvicorn
echo "Starting Django application..."
uvicorn core.asgi:application --host 0.0.0.0 --port 8000

