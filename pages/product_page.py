from selenium.webdriver.common.by import By
from pages.base import BasePage

class ProductPage(BasePage):
    TITLE_H1 = (By.CSS_SELECTOR, "#content h1")
    BUTTON_CART = (By.CSS_SELECTOR, "#button-cart")
    QTY = (By.CSS_SELECTOR, "#input-quantity")
    TABS = (By.CSS_SELECTOR, ".nav-tabs")
    PRICE_BLOCK = (By.CSS_SELECTOR, "#content .price, .product-price, .list-unstyled h2")

    def open_by_id(self, base_url: str, path: str = "57", product_id: str = "49"):
        url = f"{base_url}/index.php?route=product/product&path={path}&product_id={product_id}"
        return self.open(url)
