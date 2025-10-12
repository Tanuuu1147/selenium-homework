# otus_02_2025

Проект с автоматизированными тестами для OpenCart с использованием Selenium и pytest.

## Структура проекта

```
.
├── pages/              # Page Object модели
├── tests/              # Тестовые сценарии
├── utils/              # Вспомогательные утилиты
├── opencart_data/      # Тестовые данные
├── conftest.py         # Конфигурация pytest и фикстуры
├── pytest.ini          # Настройки pytest
├── requirements.txt    # Python зависимости
└── Dockerfile          # Docker образ для запуска тестов
```

## Установка

### Локальная установка

```bash
pip install -r requirements.txt
```

### Запуск с Docker

```bash
# Сборка образа
docker build -t tests .

# Запуск тестов
docker run -it tests --browser firefox tests/test_allure_smoke.py
```

## Использование

### Локальный запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с выбором браузера
pytest --browser firefox

# Запуск конкретного теста
pytest tests/test_main_page_po.py --browser chrome
```

### Запуск в Docker

```bash
# Простой запуск
docker run -it tests --browser firefox tests/test_catalog_po.py

# С параметрами
docker run -it tests --browser firefox --base-url https://demo.opencart.com tests/

# С сохранением Allure результатов
docker run -it -v $(pwd)/allure-results:/app/allure-results tests --browser firefox
```

## Docker

Подробная документация по Docker:
- **[SOLUTION.md](SOLUTION.md)** - описание решения задачи с Dockerfile
- **[README_DOCKER_RU.md](README_DOCKER_RU.md)** - полное руководство на русском
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - быстрый старт
- **[DOCKER_EXAMPLES.md](DOCKER_EXAMPLES.md)** - примеры команд

## Параметры запуска

- `--browser` - выбор браузера (chrome | firefox | safari)
- `--base-url` - базовый URL OpenCart
- `--admin-path` - путь к админ-панели
- `--admin-username` - имя администратора
- `--admin-password` - пароль администратора
- `--headless` - запуск в headless режиме

## Генерация отчетов Allure

```bash
# Запуск тестов с генерацией результатов
pytest --alluredir=allure-results

# Генерация отчета
allure generate allure-results -o allure-report --clean

# Открытие отчета
allure open allure-report
```

## Особенности

- ✅ Page Object Pattern
- ✅ Pytest фикстуры для браузеров
- ✅ Поддержка Chrome, Firefox, Safari
- ✅ Allure отчеты
- ✅ Docker поддержка
- ✅ Headless режим
- ✅ Параметризация тестов
- ✅ Логирование