from utils.waits import wait_element, wait_all, wait_title

def test_main_page_elements(browser, base_url):
    browser.get(base_url)

    wait_title(browser, "Your Store")                          # 1 заголовок
    wait_element(browser, "#logo")                             # 2 логотип
    wait_element(browser, "input[name='search']")              # 3 поиск
    wait_element(browser, "#cart, .btn-inverse, .dropdown-cart, a[title*='Shopping Cart'], a[title*='Корзина']")  # 4 корзина
    wait_all(browser, ".product-thumb, .product-layout")       # 5 карточки товаров
