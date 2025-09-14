from selenium.webdriver.common.by import By
from utils.waits import wait_element, wait_all

def test_product_page(browser, base_url):

    browser.get(base_url + "/index.php?route=product/product&path=57&product_id=49")
    wait_element(browser, "#content h1")
    wait_element(browser, "#button-cart")
    wait_element(browser, "#input-quantity")
    wait_element(browser, ".nav-tabs")
    wait_element(browser, "#content .price, .product-price, .list-unstyled h2")
