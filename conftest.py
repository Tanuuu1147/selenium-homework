# conftest.py
import os
import pytest
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait

import allure
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome",
                     help="chrome | firefox | safari")
    parser.addoption("--base-url", action="store", default="https://demo.opencart.com",
                     help="Base URL of OpenCart")
    parser.addoption("--admin-path", action="store", default="/administration",
                     help="Path to admin login page (/administration или /admin)")
    parser.addoption("--admin-username", action="store", default=os.getenv("OC_ADMIN_USER", ""),
                     help="Admin username")
    parser.addoption("--admin-password", action="store", default=os.getenv("OC_ADMIN_PASS", ""),
                     help="Admin password")
    parser.addoption("--headless", action="store_true", default=False,
                     help="Run browser in headless mode")


@pytest.fixture(scope="session")
def base_url(request):
    url = request.config.getoption("--base-url").rstrip("/")
    logger.info(f"Используется базовый URL: {url}")
    return url


@pytest.fixture(scope="session")
def admin_path(request):
    path = request.config.getoption("--admin-path")
    path = path if path.startswith("/") else "/" + path
    logger.info(f"Используется путь к админке: {path}")
    return path


@pytest.fixture(scope="session")
def admin_creds(request):
    creds = {
        "user": request.config.getoption("--admin-username"),
        "password": request.config.getoption("--admin-password"),
    }
    logger.info(f"Используются креды админа: user={creds['user']}, password={'*' * len(creds['password'])}")
    return creds


@pytest.fixture
def browser(request):
    name = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")
    
    logger.info(f"Инициализация браузера: {name}, headless: {headless}")

    if name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            logger.info("Chrome запускается в headless режиме")
        options.add_argument("--window-size=1920,1080")

      
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--lang=en-US")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "autofill.profile_enabled": False,
            "translate_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
        }
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=options)

    elif name == "firefox":
        fopts = FirefoxOptions()
        if headless:
            fopts.add_argument("-headless")
            logger.info("Firefox запускается в headless режиме")
        driver = webdriver.Firefox(service=FirefoxService(), options=fopts)
        driver.set_window_size(1920, 1080)

    elif name == "safari":
        driver = webdriver.Safari()
        logger.info("Safari запущен")
    else:
        logger.error(f"Неизвестный браузер: {name}")
        raise pytest.UsageError(f"Unknown --browser={name}")

    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)
    
    logger.info(f"Браузер {name} успешно инициализирован")
    yield driver
    
    logger.info(f"Закрытие браузера {name}")
    driver.quit()


@pytest.fixture
def wait(browser):
    """Явные ожидания по умолчанию"""
    return WebDriverWait(browser, 10)


def _ts():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        logger.error(f"Тест упал: {item.name}")
        drv = item.funcargs.get("browser")
        if not drv:
            return
        
        
        try:
            screenshot = drv.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"screenshot-{_ts()}",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.info("Скриншот добавлен в отчет")
        except Exception as e:
            logger.warning(f"Не удалось сделать скриншот: {str(e)}")
        
        
        try:
            current_url = drv.current_url
            allure.attach(
                current_url,
                name=f"url-{_ts()}",
                attachment_type=allure.attachment_type.TEXT,
            )
            logger.info(f"URL добавлен в отчет: {current_url}")
        except Exception as e:
            logger.warning(f"Не удалось получить URL: {str(e)}")
        
        
        try:
            page_source = drv.page_source
            allure.attach(
                page_source,
                name=f"page-source-{_ts()}",
                attachment_type=allure.attachment_type.HTML,
            )
            logger.info("HTML код страницы добавлен в отчет")
        except Exception as e:
            logger.warning(f"Не удалось получить HTML: {str(e)}")
        
    
        try:
            logs = drv.get_log("browser")
            text = "\n".join([str(l) for l in logs]) or "browser log is empty"
            allure.attach(
                text,
                name=f"browser-logs-{_ts()}",
                attachment_type=allure.attachment_type.TEXT,
            )
            logger.info("Логи браузера добавлены в отчет")
        except Exception as e:
            logger.debug(f"Не удалось получить логи браузера: {str(e)}")
