from pages.product_page import ProductPage

def test_product_page_po(browser, base_url):
    page = ProductPage(browser).open_by_id(base_url, path="57", product_id="49")
    page.wait_visible(ProductPage.TITLE_H1)
    page.wait_visible(ProductPage.BUTTON_CART)
    page.wait_visible(ProductPage.QTY)
    page.wait_visible(ProductPage.TABS)
    page.wait_visible(ProductPage.PRICE_BLOCK)
