import pytest
import time
from pages.login_page import LoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage
from pages.admin.admin_products_page import AdminProductsPage

@pytest.mark.admin
def test_admin_add_product_po(browser, base_url, admin_path, admin_creds):
    if not admin_creds["user"] or not admin_creds["password"]:
        pytest.skip("Нужны --admin-username и --admin-password")

    # логин
    LoginPage(browser).open_admin(base_url, admin_path).login(admin_creds["user"], admin_creds["password"])
    AdminDashboardPage(browser).is_opened()

    # add
    products = AdminProductsPage(browser).open_products(base_url, admin_path)
    uniq = str(int(time.time()))
    alert = products.add_product(name=f"PO Test {uniq}", meta="PO Meta", model=f"PO-{uniq}")
    assert "Success" in alert.text

@pytest.mark.admin
def test_admin_delete_first_product_po(browser, base_url, admin_path, admin_creds):
    if not admin_creds["user"] or not admin_creds["password"]:
        pytest.skip("Нужны --admin-username и --admin-password")

    # логин
    LoginPage(browser).open_admin(base_url, admin_path).login(admin_creds["user"], admin_creds["password"])
    AdminDashboardPage(browser).is_opened()

    # delete first
    products = AdminProductsPage(browser).open_products(base_url, admin_path)
    alert = products.delete_first_product()
    assert "Success" in alert.text
