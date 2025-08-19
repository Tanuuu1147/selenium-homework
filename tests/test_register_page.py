from selenium.webdriver.common.by import By
from utils.waits import wait_element

def test_register_page(browser, base_url):
    browser.get(base_url + "/index.php?route=account/register")
    wait_element(browser, "#content h1")                 # 1 заголовок
    wait_element(browser, "#input-firstname")            # 2
    wait_element(browser, "#input-lastname")             # 3
    wait_element(browser, "#input-email")                # 4
    wait_element(browser, "#input-password")             # 5
    wait_element(browser, "input[name='agree']")         # 6 чекбокс политики
    wait_element(browser, "input[type='submit'], button[type='submit']")  # 7 сабмит
