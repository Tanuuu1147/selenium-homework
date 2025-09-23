from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.base import BasePage

class AdminDashboardPage(BasePage):
   
    MENU = (By.CSS_SELECTOR, "#menu, .navbar, .sidebar, #column-left, .main-menu")
    LOGOUT = (By.CSS_SELECTOR, "a[href*='logout'], .logout, button[onclick*='logout']")
    DASHBOARD_CONTENT = (By.CSS_SELECTOR, "#content, .content, .main-content, .dashboard")

    def is_opened(self):
        """Проверяем что админская панель открыта"""
        try:
            
            return (self.wait_visible(self.MENU, timeout=5) or 
                   self.wait_visible(self.DASHBOARD_CONTENT, timeout=5))
        except TimeoutException:
            admin_indicators = [
                "#header", ".header", ".navbar-brand",
                "[href*='dashboard']", "[href*='admin']",
                ".btn-group", ".breadcrumb"
            ]
            for selector in admin_indicators:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    return elements[0]
            
            raise AssertionError("Не удалось подтвердить загрузку админской панели")

    def logout(self):
        """Выход из админки"""
        self.click(self.LOGOUT)
