import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait


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
    return request.config.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="session")
def admin_path(request):
    path = request.config.getoption("--admin-path")
    return path if path.startswith("/") else "/" + path


@pytest.fixture(scope="session")
def admin_creds(request):
    return {
        "user": request.config.getoption("--admin-username"),
        "password": request.config.getoption("--admin-password"),
    }


@pytest.fixture
def browser(request):
    """Фикстура для запуска браузера"""
    name = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    if name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,900")
        driver = webdriver.Chrome(service=ChromeService(), options=options)

    elif name == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(service=FirefoxService(), options=options)
        driver.set_window_size(1280, 900)

    elif name == "safari":
        driver = webdriver.Safari()

    else:
        raise pytest.UsageError(f"Unknown --browser={name}")

    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


@pytest.fixture
def wait(browser):
    """Явные ожидания по умолчанию"""
    return WebDriverWait(browser, 10)
