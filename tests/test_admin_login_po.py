import pytest
from pages.login_page import LoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage

@pytest.mark.admin
def test_admin_login_page_po(browser, base_url, admin_path, admin_creds):
    if not admin_creds["user"] or not admin_creds["password"]:
        pytest.skip("Нужны --admin-username и --admin-password")

    login_page = LoginPage(browser).open_admin(base_url, admin_path)

    login_page.login(admin_creds["user"], admin_creds["password"])

    dashboard = AdminDashboardPage(browser)
    dashboard.is_opened()

    dashboard.logout()

    login_page.wait_visible(LoginPage.USERNAME)
    login_page.wait_visible(LoginPage.PASSWORD)
