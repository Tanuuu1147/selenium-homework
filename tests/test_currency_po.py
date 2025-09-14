import pytest
from pages.components.currency_dropdown import CurrencyDropdown
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

@pytest.mark.parametrize("currency_name,currency_symbol", [
    ("€ Euro", "€"),
    ("£ Pound Sterling", "£"),
    ("$ US Dollar", "$"),
])
def test_currency_switch_po(browser, base_url, wait, currency_name, currency_symbol):
    dropdown = CurrencyDropdown(browser).open(base_url + "/")
    dropdown.choose_currency(currency_name)

    def has_symbol(driver):
        elems = driver.find_elements(By.CSS_SELECTOR, ".product-thumb .price, .price")
        for e in elems:
            try:
                if currency_symbol in ((e.text or "").strip()):
                    return True
            except StaleElementReferenceException:
                continue
        return False

    wait.until(has_symbol)
