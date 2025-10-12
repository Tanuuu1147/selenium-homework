# Используем официальный Python 3.11 образ
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .
COPY pytest.ini .
COPY conftest.py .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

ENV SE_AVOID_STATS=true

# Копирование исходного кода проекта
COPY pages/ ./pages/
COPY tests/ ./tests/
COPY utils/ ./utils/
COPY opencart_data/ ./opencart_data/



# Создание директории для allure результатов
RUN mkdir -p allure-results

# Запуск тестов по умолчанию
CMD ["pytest"]