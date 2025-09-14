from selenium.webdriver.common.by import By
from pages.base import BasePage

class CurrencyDropdown(BasePage):
    TOGGLE = (By.CSS_SELECTOR, "#form-currency .dropdown-toggle")
    MENU = (By.CSS_SELECTOR, "#form-currency .dropdown-menu")

    def choose_currency(self, currency_name: str):
        self.click(self.TOGGLE)
        self.wait_visible(self.MENU)
        self.click((By.XPATH, f"//form[@id='form-currency']//a[contains(normalize-space(.), '{currency_name}')]"))
