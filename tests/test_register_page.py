from selenium.webdriver.common.by import By
from utils.waits import wait_element

def test_register_page(browser, base_url):
    browser.get(base_url + "/index.php?route=account/register")
    wait_element(browser, "#content h1")
    wait_element(browser, "#input-firstname")
    wait_element(browser, "#input-lastname")
    wait_element(browser, "#input-email")
    wait_element(browser, "#input-password")
    wait_element(browser, "input[name='agree']")
    wait_element(browser, "input[type='submit'], button[type='submit']")
