from utils.waits import wait_element

def test_admin_login_page(browser, base_url):
    browser.get(base_url + "/administration")
    if "administration" not in browser.current_url:
        browser.get(base_url + "/admin")

    wait_element(browser, "#input-username")
    wait_element(browser, "#input-password")
    wait_element(browser, "button[type='submit']")
    wait_element(browser, "form")
    assert "Administration" in browser.title
