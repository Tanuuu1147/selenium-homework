from utils.waits import wait_element, wait_all, wait_title

def test_main_page_elements(browser, base_url):
    browser.get(base_url)

    wait_title(browser, "Your Store")
    wait_element(browser, "#logo")
    wait_element(browser, "input[name='search']")
    wait_element(browser, "#cart, .btn-inverse, .dropdown-cart, a[title*='Shopping Cart'], a[title*='Корзина']")
    wait_all(browser, ".product-thumb, .product-layout")
