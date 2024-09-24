# Используем официальный образ Python 3.9
FROM python:3.9-slim

# Устанавливаем зависимости для PostgreSQL, Kerberos и других компонентов
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    libkrb5-dev \
    krb5-user

# Устанавливаем рабочую директорию для приложения
WORKDIR /src

# Копируем файлы приложения в контейнер
COPY . /src

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для Flask
EXPOSE 5000
# Запуск Flask приложения через Gunicorn и параллельный запуск main.py
CMD ["sh", "-c", "python main.py & gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app"]