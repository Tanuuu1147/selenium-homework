from selenium.webdriver.common.by import By
from utils.waits import wait_element, wait_all

def test_catalog_page(browser, base_url):
    # Пример: Desktops (path=20)
    browser.get(base_url + "/index.php?route=product/category&path=20")
    wait_element(browser, ".breadcrumb")                    # 1
    wait_element(browser, ".list-group")                    # 2 (левое меню)
    wait_element(browser, "#input-sort")                    # 3 (сортировка)
    wait_element(browser, "#input-limit")                   # 4 (лимит)
    wait_all(browser, ".product-layout, .product-thumb")    # 5 (товарные карточки)
