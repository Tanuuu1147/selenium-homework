import time
import pytest
from pages.register_page import RegisterPage

def test_register_new_user_po(browser, base_url):
    email = f"user_{int(time.time())}@mail.com"
    page = RegisterPage(browser).open_register(base_url)
    try:
        heading = page.register("Test", "User", email, "password123")
    except AssertionError as e:
        pytest.fail(f"Регистрация не удалась: {e}")

    assert "Your Account Has Been Created!" in heading.text
