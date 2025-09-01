from selenium.webdriver.common.by import By
from pages.base import BasePage

class AdminLoginPage(BasePage):
    USER = (By.CSS_SELECTOR, "#input-username")
    PASS = (By.CSS_SELECTOR, "#input-password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    FORM = (By.CSS_SELECTOR, "form")

    def open_admin(self, base_url: str, admin_path: str = "/administration"):
        path = admin_path if admin_path.startswith("/") else f"/{admin_path}"
        return self.open(base_url + path)

    def is_opened(self) -> bool:
        self.wait_visible(self.USER)
        self.wait_visible(self.PASS)
        self.wait_visible(self.SUBMIT)
        self.wait_visible(self.FORM)
        return "Administration" in (self.driver.title or "")

    def login(self, username: str, password: str):
        self.type(self.USER, username)
        self.type(self.PASS, password)
        self.click(self.SUBMIT)
        return self
