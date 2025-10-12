import pytest
import time
import logging
import allure
from pages.login_page import LoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage
from pages.admin.admin_products_page import AdminProductsPage

logger = logging.getLogger(__name__)

@allure.epic("Админ панель")
@allure.feature("Управление продуктами")
@allure.story("Добавление продукта")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.admin
def test_admin_add_product_po(browser, base_url, admin_path, admin_creds):
    """Тест добавления нового продукта через админ панель"""
    if not admin_creds["user"] or not admin_creds["password"]:
        pytest.skip("Нужны --admin-username и --admin-password")

    logger.info("=== Начало теста добавления продукта ===")
    
    with allure.step("Авторизация в админ панели"):
        logger.info(f"Авторизация пользователя: {admin_creds['user']}")
        LoginPage(browser).open_admin(base_url, admin_path).login(admin_creds["user"], admin_creds["password"])
        AdminDashboardPage(browser).is_opened()

    with allure.step("Переход к управлению продуктами"):
        products = AdminProductsPage(browser).open_products(base_url, admin_path)

    with allure.step("Добавление нового продукта"):
        uniq = str(int(time.time()))
        product_name = f"PO Test {uniq}"
        product_model = f"PO-{uniq}"
        
        logger.info(f"Создание продукта: {product_name}, модель: {product_model}")
        allure.attach(product_name, "Название продукта", allure.attachment_type.TEXT)
        allure.attach(product_model, "Модель продукта", allure.attachment_type.TEXT)
        
        alert = products.add_product(name=product_name, meta="PO Meta", model=product_model)

    with allure.step("Проверка успешного создания продукта"):
        assert "Success" in alert.text, f"Ожидали 'Success' в тексте алерта, получили: {alert.text}"
        logger.info("Продукт успешно создан")

@allure.epic("Админ панель")
@allure.feature("Управление продуктами")
@allure.story("Удаление продукта")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.admin
def test_admin_delete_first_product_po(browser, base_url, admin_path, admin_creds):
    """Тест удаления первого продукта из списка"""
    if not admin_creds["user"] or not admin_creds["password"]:
        pytest.skip("Нужны --admin-username и --admin-password")

    logger.info("=== Начало теста удаления продукта ===")
    
    with allure.step("Авторизация в админ панели"):
        logger.info(f"Авторизация пользователя: {admin_creds['user']}")
        LoginPage(browser).open_admin(base_url, admin_path).login(admin_creds["user"], admin_creds["password"])
        AdminDashboardPage(browser).is_opened()

    with allure.step("Переход к управлению продуктами"):
        products = AdminProductsPage(browser).open_products(base_url, admin_path)

    with allure.step("Удаление первого продукта"):
        logger.info("Удаление первого продукта из списка")
        alert = products.delete_first_product()

    with allure.step("Проверка успешного удаления продукта"):
        assert "Success" in alert.text, f"Ожидали 'Success' в тексте алерта, получили: {alert.text}"
        logger.info("Продукт успешно удален")
