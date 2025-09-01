from selenium.webdriver.common.by import By
from pages.base import BasePage

class MainPage(BasePage):
    TITLE = "Your Store"
    LOGO = (By.CSS_SELECTOR, "#logo")
    SEARCH = (By.CSS_SELECTOR, "input[name='search']")
    CART = (By.CSS_SELECTOR, "#cart, .btn-inverse, .dropdown-cart, a[title*='Shopping Cart'], a[title*='Корзина']")
    PRODUCT_TILES = (By.CSS_SELECTOR, ".product-thumb, .product-layout")

    def open_home(self, base_url):
        return self.open(base_url)
