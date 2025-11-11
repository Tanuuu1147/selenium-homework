# Используем готовый образ Python
FROM python:3.11

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    xvfb \
    libxi6 \
    libnss3 \
    libxss1 \
    fonts-liberation \
    libasound2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование конфигурационных файлов
COPY pytest.ini .
COPY conftest.py .

# Копирование исходного кода проекта
COPY pages/ ./pages/
COPY tests/ ./tests/
COPY utils/ ./utils/
COPY opencart_data/ ./opencart_data/

# Создание директории для allure результатов с правильными правами
RUN mkdir -p /app/allure-results && chmod 777 /app/allure-results

# Копирование entrypoint скрипта
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Установка entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Запуск тестов по умолчанию
CMD ["--browser", "chrome"]