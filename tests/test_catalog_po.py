from pages.category_page import CategoryPage

def test_catalog_page_po(browser, base_url):
    page = CategoryPage(browser).open_by_path(base_url, "20")
    page.wait_visible(CategoryPage.BREADCRUMB)
    page.wait_visible(CategoryPage.LEFT_MENU)
    page.wait_visible(CategoryPage.SORT)
    page.wait_visible(CategoryPage.LIMIT)
    page.wait_visible(CategoryPage.PRODUCT_TILES)
