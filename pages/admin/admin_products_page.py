from selenium.webdriver.common.by import By
from pages.base import BasePage

class AdminProductsPage(BasePage):
    MENU_CATALOG = (By.ID, "menu-catalog")
    PRODUCTS_LINK = (By.LINK_TEXT, "Products")
    ADD_BUTTON = (By.CSS_SELECTOR, "a[data-original-title='Add New'], .btn-primary")
    DELETE_BUTTON = (By.CSS_SELECTOR, "button[data-original-title='Delete'], .btn-danger")
    SAVE_BUTTON = (By.CSS_SELECTOR, "button[data-original-title='Save'], .btn-primary")
    SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert-success")

    # поля товара
    NAME_INPUT = (By.CSS_SELECTOR, "#input-name1")
    META_TITLE_INPUT = (By.CSS_SELECTOR, "#input-meta-title1")
    MODEL_INPUT = (By.CSS_SELECTOR, "#input-model")

    def open_products(self, base_url, admin_path):
        self.open(base_url + admin_path)
        # открыть "Catalog → Products"
        self.click(self.MENU_CATALOG)
        self.click(self.PRODUCTS_LINK)
        return self

    def add_product(self, name="Test Product", meta="Test Meta", model="TP123"):
        self.click(self.ADD_BUTTON)
        self.type(self.NAME_INPUT, name)
        self.type(self.META_TITLE_INPUT, meta)
        self.click((By.LINK_TEXT, "Data"))
        self.type(self.MODEL_INPUT, model)
        self.click(self.SAVE_BUTTON)
        return self.wait_visible(self.SUCCESS_ALERT)

    def delete_first_product(self):
        # кликнуть чекбокс в первой строке таблицы
        checkbox = self.wait_visible((By.CSS_SELECTOR, "table tbody tr:first-child input[type='checkbox']"))
        self.driver.execute_script("arguments[0].click();", checkbox)
        self.click(self.DELETE_BUTTON)
        alert = self.driver.switch_to.alert
        alert.accept()
        return self.wait_visible(self.SUCCESS_ALERT)
