from selenium.webdriver.common.by import By
from pages.base import BasePage

class CategoryPage(BasePage):
    BREADCRUMB = (By.CSS_SELECTOR, ".breadcrumb")
    LEFT_MENU = (By.CSS_SELECTOR, ".list-group")
    SORT = (By.CSS_SELECTOR, "#input-sort")
    LIMIT = (By.CSS_SELECTOR, "#input-limit")
    PRODUCT_TILES = (By.CSS_SELECTOR, ".product-layout, .product-thumb")

    def open_by_path(self, base_url: str, path: str = "20"):
        url = f"{base_url}/index.php?route=product/category&path={path}"
        return self.open(url)

