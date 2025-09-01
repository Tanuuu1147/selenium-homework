from selenium.webdriver.common.by import By
from pages.base import BasePage

class AdminDashboardPage(BasePage):
    MENU = (By.ID, "menu")
    LOGOUT = (By.CSS_SELECTOR, "a[href*='logout']")

    def is_opened(self):
        return self.wait_visible(self.MENU)

    def logout(self):
        self.click(self.LOGOUT)
