# Используйте официальный образ Python
FROM python:3.10

# Установите рабочую директорию в контейнере
WORKDIR /

# Копируйте файлы зависимостей и установите зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-telegram-bot[webhooks]


# Копируйте остальные файлы проекта
COPY . .

# Укажите команду для запуска при старте контейнера
CMD ["python", "bot.py"]
