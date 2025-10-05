# conftest.py
import pytest
from selenium import webdriver

def pytest_addoption(parser):
    parser.addoption("--executor", default="selenoid")  # local | selenoid
    parser.addoption("--browser", default="chrome")
    parser.addoption("--browser-version", default="124.0")
    parser.addoption("--selenoid", default="http://127.0.0.1:4444/wd/hub")
    parser.addoption("--timeout", type=int, default=120)

@pytest.fixture
def driver(request):
    executor = request.config.getoption("--executor")
    browser = request.config.getoption("--browser").lower()
    version = request.config.getoption("--browser-version")
    selenoid_url = request.config.getoption("--selenoid")
    timeout = request.config.getoption("--timeout")

    # --- локально ---
    if executor == "local":
        if browser == "chrome":
            drv = webdriver.Chrome()
        elif browser == "firefox":
            drv = webdriver.Firefox()
        else:
            raise RuntimeError(f"Unsupported local browser: {browser}")
        yield drv
        drv.quit()
        return

    # --- удалённо (Selenoid) ---
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        # важно для контейнеров
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
    else:
        raise RuntimeError(f"Unsupported remote browser: {browser}")

    options.set_capability("browserName", browser)
    options.set_capability("browserVersion", version)
    options.set_capability("platformName", "linux")
    options.set_capability(
        "selenoid:options",
        {
            "enableVNC": True,
            "enableVideo": False,
            "sessionTimeout": f"{timeout}s",
        },
    )

    drv = webdriver.Remote(command_executor=selenoid_url, options=options)
    yield drv
    drv.quit()
