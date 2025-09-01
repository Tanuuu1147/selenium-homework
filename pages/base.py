# pages/base.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver, base_url=None):
        self.driver = driver
        self.base_url = base_url

    def open(self, url):
        self.driver.get(url)
        return self

    def wait_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_clickable(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def click(self, locator):
        el = self.wait_clickable(locator)
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)

    def type(self, locator, text):
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)
