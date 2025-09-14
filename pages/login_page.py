from selenium.webdriver.common.by import By
from pages.base import BasePage

class LoginPage(BasePage):
    USERNAME = (By.ID, "input-username")
    PASSWORD = (By.ID, "input-password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    def open_admin(self, base_url, admin_path):
        return self.open(base_url + admin_path)

    def login(self, user, password):
        self.type(self.USERNAME, user)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)
