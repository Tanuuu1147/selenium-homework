
# utils/waits.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def wait_element(driver, selector, by=By.CSS_SELECTOR, timeout=7):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )
    except TimeoutException:
        driver.save_screenshot(f"{driver.session_id}.png")
        raise AssertionError(f"Не дождался элемента: {selector}")

def wait_all(driver, selector, by=By.CSS_SELECTOR, timeout=7):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_all_elements_located((by, selector))
        )
    except TimeoutException:
        driver.save_screenshot(f"{driver.session_id}.png")
        raise AssertionError(f"Не дождался списка элементов: {selector}")

def wait_title(driver, title, timeout=7):
    try:
        WebDriverWait(driver, timeout).until(EC.title_is(title))
    except TimeoutException:
        raise AssertionError(f"Ожидал title='{title}', а был '{driver.title}'")
