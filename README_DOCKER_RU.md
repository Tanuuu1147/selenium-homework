# Dockerfile для проекта с Selenium тестами OpenCart

## Описание задачи

Создан рабочий Dockerfile для запуска Selenium тестов в контейнере Docker с возможностью передачи параметров при запуске.

## Файлы проекта

### Основные файлы
- **Dockerfile** - основной рабочий Dockerfile с Firefox и Geckodriver
- **.dockerignore** - исключения для Docker сборки
- **DOCKER_QUICKSTART.md** - краткое руководство по использованию
- **DOCKER_EXAMPLES.md** - примеры команд запуска
- **README_DOCKER.md** - подробная документация (англ.)

### Альтернативные Dockerfile
- **Dockerfile.firefox** - облегченная версия только с Firefox
- **Dockerfile.simple** - упрощенная версия с Chrome через .deb
- **Dockerfile.minimal** - минимальная версия
- **Dockerfile.selenium** - версия на базе образа selenium/standalone-chrome

## Возможности

✅ Запуск Selenium тестов в изолированном контейнере  
✅ Поддержка Firefox браузера (ESR версия)  
✅ Автоматическая установка Geckodriver для ARM64 и AMD64  
✅ Headless режим через Xvfb  
✅ Передача всех параметров из conftest.py  
✅ Поддержка Allure отчетов  
✅ Работа на macOS (Apple Silicon) и Linux  

## Быстрый старт

### 1. Сборка образа
```bash
docker build -t tests .
```

### 2. Запуск тестов

```bash
# Простой smoke test
docker run -it tests tests/test_allure_smoke.py --browser firefox

# Запуск с параметрами
docker run -it tests --browser firefox tests/test_catalog_po.py --base-url https://demo.opencart.com
```

## Поддерживаемые параметры

Все параметры из `conftest.py` поддерживаются:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--browser` | Браузер (firefox) | firefox |
| `--base-url` | Базовый URL | https://demo.opencart.com |
| `--admin-path` | Путь к админке | /administration |
| `--admin-username` | Имя администратора | - |
| `--admin-password` | Пароль администратора | - |
| `--headless` | Headless режим | true |

## Примеры использования

### Выбор браузера
```bash
docker run -it tests --browser firefox tests/test_catalog_po.py
```

### Указание базового URL
```bash
docker run -it tests --browser firefox --base-url https://demo.opencart.com tests/test_main_page_po.py
```

### Verbose режим
```bash
docker run -it tests -v tests/test_catalog_po.py --browser firefox
```

### Сохранение Allure результатов
```bash
mkdir -p allure-results
docker run -it -v $(pwd)/allure-results:/app/allure-results tests --browser firefox tests/
```

### Передача переменных окружения
```bash
docker run -it \
  -e OC_ADMIN_USER=demo \
  -e OC_ADMIN_PASS=demo \
  tests --browser firefox tests/test_admin_login_po.py
```

## Архитектура решения

### Структура Dockerfile

1. **Базовый образ**: `python:3.11-slim`
2. **Системные зависимости**: wget, curl, xvfb, firefox-esr
3. **Geckodriver**: автоматическая установка для текущей архитектуры
4. **Python зависимости**: установка из requirements.txt
5. **Исходный код**: копирование всех необходимых файлов
6. **Entrypoint**: скрипт для запуска Xvfb и pytest

### Особенности реализации

- **Multi-arch поддержка**: автоматическое определение архитектуры (ARM64/AMD64) и установка соответствующего Geckodriver
- **Xvfb**: виртуальный дисплей для headless режима
- **Патчинг conftest.py**: явное указание пути к Geckodriver для обхода ограничений Selenium Manager
- **Переменные окружения**: настройка PATH и DISPLAY для корректной работы

## Проверка работоспособности

### Проверка сборки
```bash
docker build -t tests .
# Должно завершиться успешно
```

### Проверка запуска
```bash
docker run -it tests tests/test_allure_smoke.py --browser firefox
# Ожидаемый результат: 1 passed
```

### Проверка передачи параметров
```bash
docker run -it tests --browser firefox --base-url https://demo.opencart.com tests/test_catalog_po.py
# Тест должен запуститься с указанным URL
```

## Устранение проблем

### Медленная сборка
- Используйте Docker BuildKit: `DOCKER_BUILDKIT=1 docker build -t tests .`
- Проверьте подключение к интернету
- Используйте кеш Docker

### Ошибки при запуске браузера
- Убедитесь, что используется флаг `--headless`
- Проверьте, что Xvfb запускается (смотрите логи entrypoint.sh)

### Ошибки с архитектурой
- Для ARM (M1/M2) используется geckodriver-v0.35.0-linux-aarch64
- Для AMD64 используется geckodriver-v0.35.0-linux64
- Установка происходит автоматически

## Технические детали

### Размер образа
Финальный размер образа: ~800MB-1GB (зависит от кеша и архитектуры)

### Используемые порты
- Нет открытых портов (все работает локально в контейнере)

### Volumes
- `/app/allure-results` - результаты тестов Allure

### Рабочая директория
- `/app` - основная рабочая директория в контейнере

## Дополнительная информация

### Логи
Логи pytest выводятся в stdout/stderr, доступны через `docker logs`

### Отладка
```bash
# Вход в контейнер для отладки
docker run -it --entrypoint /bin/bash tests

# Проверка версий
docker run -it --entrypoint /bin/bash tests -c "python --version && firefox --version && geckodriver --version"
```

### Очистка
```bash
# Удаление образа
docker rmi tests

# Очистка неиспользуемых образов
docker image prune -a
```

## Критерии приемки

✅ В проекте есть работающий Dockerfile  
✅ Образ успешно собирается командой `docker build -t tests .`  
✅ Тесты запускаются командой `docker run -it tests`  
✅ Поддерживается передача параметров (например, `--browser firefox`)  
✅ Опции из conftest.py корректно работают в контейнере  

## Автор
Проект с тестами для OpenCart с использованием Selenium и Docker