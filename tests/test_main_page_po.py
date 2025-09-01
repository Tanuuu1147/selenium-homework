from pages.main_page import MainPage

def test_main_page_elements_po(browser, base_url):
    page = MainPage(browser).open_home(base_url)
    page.wait_visible(MainPage.LOGO)
    page.wait_visible(MainPage.SEARCH)
    page.wait_visible(MainPage.CART)
    page.wait_visible(MainPage.PRODUCT_TILES)
    assert browser.title == MainPage.TITLE
