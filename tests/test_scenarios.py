import random
import re
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# ==================== helpers ====================

def _scroll_into_view(driver, el):
    """Прокручивает страницу так, чтобы элемент оказался в центре."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)


def _safe_click(driver, el):
    """Надёжный клик через JS (если обычный не срабатывает)."""
    driver.execute_script("arguments[0].click();", el)


def _get_cart_indicator_text(driver) -> str:
    """Возвращает текст из индикатора корзины (разные темы OpenCart)."""
    candidates = [
        (By.CSS_SELECTOR, "#cart-total"),
        (By.CSS_SELECTOR, "#cart .dropdown-toggle"),
        (By.CSS_SELECTOR, "#header-cart .dropdown-toggle"),
        (By.CSS_SELECTOR, "#cart > button"),
    ]
    for by, sel in candidates:
        els = driver.find_elements(by, sel)
        if els:
            try:
                txt = (els[0].text or "").strip()
                if txt:
                    return txt
            except Exception:
                pass
    return ""


def _get_cart_count(driver) -> int:
    """
    Пытаемся вытащить число товаров из текста индикатора.
    Примеры: "0 item(s) - $0.00", "Cart (2)" и т.п.
    """
    txt = _get_cart_indicator_text(driver)
    m = re.search(r"(\d+)\s*item", txt, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"\((\d+)\)", txt)
    if m:
        return int(m.group(1))
    return 0


def _open_currency_menu(wait: WebDriverWait):
    toggle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#form-currency .dropdown-toggle")))
    toggle.click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#form-currency .dropdown-menu")))


def _choose_currency(wait: WebDriverWait, currency_name: str):
    option = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//form[@id='form-currency']//a[contains(normalize-space(.), '{currency_name}')]"
    )))
    option.click()  # страница перезагрузится


def _wait_price_has_symbol(wait: WebDriverWait, css_scope: str, symbol: str):
    """Ждём, пока цены на странице обновятся и содержат нужный символ валюты."""
    def _probe(driver):
        try:
            elems = driver.find_elements(
                By.CSS_SELECTOR,
                f"{css_scope} .price, {css_scope} .product-thumb .price"
            )
            for e in elems:
                try:
                    if symbol in (e.text or ""):
                        return True
                except StaleElementReferenceException:
                    return False
            return False
        except StaleElementReferenceException:
            return False

    wait.until(_probe)


def _fill_required_options_on_product_page(driver):
    """
    На странице товара заполняем обязательные опции:
    - select: выбираем 'Red', если есть; иначе первый непустой вариант
    - radio/checkbox: кликаем первый доступный
    """
    # selects
    for sel in driver.find_elements(By.CSS_SELECTOR, ".form-group.required select"):
        try:
            s = Select(sel)
            red_idx = None
            first_non_empty = None
            for i, opt in enumerate(s.options):
                val = (opt.get_attribute("value") or "").strip()
                text = (opt.text or "").strip().lower()
                if val and first_non_empty is None:
                    first_non_empty = i
                if "red" in text:
                    red_idx = i
            idx = red_idx if red_idx is not None else (first_non_empty or 0)
            s.select_by_index(idx)
        except Exception:
            pass

    # radios / checkboxes
    for css in (".form-group.required input[type='radio']",
                ".form-group.required input[type='checkbox']"):
        opts = driver.find_elements(By.CSS_SELECTOR, css)
        if opts:
            try:
                driver.execute_script("arguments[0].click();", opts[0])
            except Exception:
                pass


def _wait_add_to_cart_feedback(driver, base_count: int, timeout: int = 6):
    """Ждём подтверждение добавления: рост счётчика либо alert-success."""
    w = WebDriverWait(driver, timeout)
    def _ok(d):
        try:
            if _get_cart_count(d) > base_count:
                return True
        except Exception:
            pass
        try:
            alerts = d.find_elements(By.CSS_SELECTOR, ".alert-success, #alert .alert-success, .toast")
            return any(a.is_displayed() for a in alerts)
        except Exception:
            return False
    w.until(_ok)


# ==================== tests ====================

# 3.1 Логин–разлогин в админку
@pytest.mark.admin
def test_admin_login_logout(browser, wait, base_url, admin_path, admin_creds):
    if not admin_creds["user"] or not admin_creds["password"]:
        pytest.skip("Нужны --admin-username и --admin-password")

    browser.get(base_url + admin_path)

    wait.until(EC.visibility_of_element_located((By.ID, "input-username"))).send_keys(admin_creds["user"])
    browser.find_element(By.ID, "input-password").send_keys(admin_creds["password"])
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.any_of(
        EC.visibility_of_element_located((By.ID, "menu")),
        EC.visibility_of_element_located((By.LINK_TEXT, "Dashboard")),
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".page-header, .panel-title"))
    ))

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='logout']"))).click()

    wait.until(EC.visibility_of_element_located((By.ID, "input-username")))
    wait.until(EC.visibility_of_element_located((By.ID, "input-password")))


# 3.2 Добавление случайного товара в корзину (через страницу товара)
def test_add_random_product_to_cart(browser, wait, base_url):
    browser.get(base_url + "/")

    # Берём любую карточку
    cards = wait.until(EC.visibility_of_all_elements_located(
        (By.CSS_SELECTOR, ".product-thumb, .product-layout")
    ))
    assert cards, "Нет товаров на главной!"
    card = random.choice(cards)

    # Достаём ссылку на страницу товара
    product_link_href = ""
    for xp in [
        ".//a[contains(@href,'route=product/product')]",
        ".//a[@href and contains(@href,'product_id=')]",
        ".//a[@href]"
    ]:
        links = card.find_elements(By.XPATH, xp)
        if links:
            try:
                href = links[0].get_attribute("href") or ""
                if href:
                    product_link_href = href
                    break
            except Exception:
                continue
    assert product_link_href, "Не нашли ссылку на страницу товара"

    # Переходим на страницу товара
    browser.get(product_link_href)

    # Заполняем обязательные опции (если есть)
    _fill_required_options_on_product_page(browser)

    # Жмём Add to Cart
    add_btn = wait.until(EC.element_to_be_clickable((By.ID, "button-cart")))
    _scroll_into_view(browser, add_btn)
    base_count = _get_cart_count(browser)
    _safe_click(browser, add_btn)

    # Ждём подтверждение
    try:
        _wait_add_to_cart_feedback(browser, base_count, timeout=6)
    except TimeoutException:
        _fill_required_options_on_product_page(browser)
        _safe_click(browser, add_btn)
        _wait_add_to_cart_feedback(browser, base_count, timeout=6)

    # Идём в корзину и проверяем, что в ней есть строки
    browser.get(base_url + "/index.php?route=checkout/cart")
    wait.until(EC.visibility_of_any_elements_located((
        By.CSS_SELECTOR,
        "#content form#cart, #content table, .table-responsive table, .cart-wrapper, .cart-total"
    )))
    rows = browser.find_elements(
        By.CSS_SELECTOR,
        "table tbody tr, #content .table tbody tr, .cart-wrapper .cart-item"
    )
    assert rows, "В корзине нет товаров после добавления!"


# 3.3 Переключение валют на главной
@pytest.mark.parametrize("currency_name,currency_symbol", [
    ("€ Euro", "€"),
    ("£ Pound Sterling", "£"),
    ("$ US Dollar", "$"),
])
def test_currency_switch_on_main(browser, wait, base_url, currency_name, currency_symbol):
    browser.get(base_url + "/")
    wait.until(EC.visibility_of_any_elements_located(
        (By.CSS_SELECTOR, ".product-thumb .price, .price")
    ))
    _open_currency_menu(wait)
    _choose_currency(wait, currency_name)
    _wait_price_has_symbol(wait, "body", currency_symbol)


# 3.4 Переключение валют в каталоге
@pytest.mark.parametrize("currency_name,currency_symbol", [
    ("€ Euro", "€"),
    ("£ Pound Sterling", "£"),
    ("$ US Dollar", "$"),
])
def test_currency_switch_in_catalog(browser, wait, base_url, currency_name, currency_symbol):
    browser.get(base_url + "/index.php?route=product/category&path=20")
    wait.until(EC.visibility_of_any_elements_located(
        (By.CSS_SELECTOR, ".product-thumb .price, .price")
    ))
    _open_currency_menu(wait)
    _choose_currency(wait, currency_name)
    _wait_price_has_symbol(wait, "#content", currency_symbol)
