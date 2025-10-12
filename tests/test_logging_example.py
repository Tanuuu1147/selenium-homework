# tests/test_logging_example.py
import pytest
import logging
import allure
from pages.main_page import MainPage

logger = logging.getLogger(__name__)

@allure.epic("Проверка логирования")
@allure.feature("Основная функциональность")
@allure.story("Открытие главной страницы")
@allure.severity(allure.severity_level.MINOR)
def test_main_page_logging_example(browser, base_url):
    """Пример теста с логированием"""
    logger.info("=== Начало теста логирования ===")
    
    with allure.step("Открытие главной страницы"):
        logger.info(f"Открытие главной страницы: {base_url}")
        page = MainPage(browser)
        page.open(base_url)
        
    with allure.step("Проверка заголовка страницы"):
        title = browser.title
        logger.info(f"Заголовок страницы: {title}")
        allure.attach(title, "Заголовок страницы", allure.attachment_type.TEXT)
        
        assert "OpenCart" in title, f"Ожидали 'OpenCart' в заголовке, получили: {title}"
        logger.info("Тест логирования успешно завершен")