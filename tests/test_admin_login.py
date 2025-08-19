from utils.waits import wait_element

def test_admin_login_page(browser, base_url):
    # Админка бывает /administration или /admin
    browser.get(base_url + "/administration")
    if "administration" not in browser.current_url:
        browser.get(base_url + "/admin")

    # 5 обязательных и стабильных проверок
    wait_element(browser, "#input-username")               # 1
    wait_element(browser, "#input-password")               # 2
    wait_element(browser, "button[type='submit']")         # 3
    wait_element(browser, "form")                          # 4
    assert "Administration" in browser.title               # 5
