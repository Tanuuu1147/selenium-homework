import random
import re
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from datetime import date, datetime
from selenium.webdriver.common.keys import Keys

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
    option.click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#form-currency .dropdown-menu")))


def _wait_price_has_symbol(wait: WebDriverWait, css_scope: str, symbol: str):
    """Ждём, пока цены на странице обновятся и содержат нужный символ валюты."""
    def _probe(driver):
        try:
            elems = driver.find_elements(
                By.CSS_SELECTOR,
                f"{css_scope} .price, {css_scope} .product-thumb .price"
            )
            if not elems:
                return False
            for e in elems:
                try:
                    txt = (e.text or "").strip()
                    if symbol in txt:
                        return True
                except StaleElementReferenceException:
                    return False
            return False
        except StaleElementReferenceException:
            return False

    wait.until(_probe)




def _fill_required_options_on_product_page(driver):
    """
    Заполняем распространённые обязательные опции товара:
    - select: первый НЕпустой
    - radio/checkbox: первый доступный
    - text/textarea: 'Test'
    - date: YYYY-MM-DD (сегодня)
    - time: HH:MM (полдень)
    - datetime-local: YYYY-MM-DDTHH:MM
    """
    # selects
    for sel in driver.find_elements(By.CSS_SELECTOR, ".form-group.required select"):
        try:
            s = Select(sel)
            for i, opt in enumerate(s.options):
                if (opt.get_attribute("value") or "").strip():
                    s.select_by_index(i)
                    break
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

    # text inputs / textarea
    for css in (".form-group.required input[type='text']",
                ".form-group.required textarea"):
        for el in driver.find_elements(By.CSS_SELECTOR, css):
            try:
                el.clear()
                el.send_keys("Test")
            except Exception:
                pass

    # date
    today = date.today().strftime("%Y-%m-%d")
    for el in driver.find_elements(By.CSS_SELECTOR, ".form-group.required input[type='date']"):
        try:
            driver.execute_script("arguments[0].value = arguments[1];", el, today)
            el.send_keys(Keys.TAB)
        except Exception:
            pass

    # time
    noon = "12:00"
    for el in driver.find_elements(By.CSS_SELECTOR, ".form-group.required input[type='time']"):
        try:
            driver.execute_script("arguments[0].value = arguments[1];", el, noon)
            el.send_keys(Keys.TAB)
        except Exception:
            pass

    # datetime-local
    dt = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")
    for el in driver.find_elements(By.CSS_SELECTOR, ".form-group.required input[type='datetime-local']"):
        try:
            driver.execute_script("arguments[0].value = arguments[1];", el, dt)
            el.send_keys(Keys.TAB)
        except Exception:
            pass




from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def _wait_add_to_cart_feedback(driver, base_count: int, timeout: int = 12):
    """Ждём подтверждение: рост счётчика, alert-success или наличие строк в мини-корзине."""
    w = WebDriverWait(driver, timeout)

    def _ok(d):
        try:
            if _get_cart_count(d) > base_count:
                return True
        except Exception:
            pass

        try:
            alerts = d.find_elements(By.CSS_SELECTOR, ".alert-success, #alert .alert-success, .toast")
            if any(a.is_displayed() for a in alerts):
                return True
        except Exception:
            pass

        try:
            btns = d.find_elements(By.CSS_SELECTOR, "#cart .dropdown-toggle, #cart > button, #header-cart .dropdown-toggle")
            if btns:
                d.execute_script("arguments[0].click();", btns[0])
                rows = d.find_elements(By.CSS_SELECTOR,
                    "#cart .table tbody tr, #header-cart .table tbody tr, .dropdown-menu .table tr, .mini-cart .table tr")
                if rows:
                    return True
        except Exception:
            pass

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
    wait.until(EC.visibility_of_any_elements_located((
        By.CSS_SELECTOR,
        ".product-thumb, .product-layout, .product-grid, .product-list, .product"
    )))

    def collect_product_hrefs(scope_css=""):
        selectors = [
            f"{scope_css} a[href*='product_id=']",
            f"{scope_css} a[href*='route=product/product']",
            f"{scope_css} .caption h4 a",
            f"{scope_css} .product-thumb a",
            f"{scope_css} .product-layout a",
        ]
        hrefs = []
        for sel in selectors:
            for a in browser.find_elements(By.CSS_SELECTOR, sel):
                try:
                    href = a.get_attribute("href") or ""
                    if "product_id=" in href or "route=product/product" in href:
                        hrefs.append(href)
                except Exception:
                    pass
        return list(dict.fromkeys(hrefs))

    hrefs = collect_product_hrefs("")
    if not hrefs:
        browser.get(base_url + "/index.php?route=product/category&path=20")
        wait.until(EC.visibility_of_any_elements_located((
            By.CSS_SELECTOR, ".product-thumb, .product-layout, .product-grid, .product-list, .product"
        )))
        hrefs = collect_product_hrefs("#content ")

    assert hrefs, "Не нашли ссылок на товары ни на главной, ни в категории"


    success = False
    errors = []

    for product_link_href in random.sample(hrefs, k=min(3, len(hrefs))):
        browser.get(product_link_href)
        _fill_required_options_on_product_page(browser)

        add_btn = wait.until(EC.element_to_be_clickable((By.ID, "button-cart")))
        _scroll_into_view(browser, add_btn)
        base_count = _get_cart_count(browser)
        _safe_click(browser, add_btn)

        try:
            _wait_add_to_cart_feedback(browser, base_count, timeout=12)
            success = True
            break
        except TimeoutException:
            try:
                _fill_required_options_on_product_page(browser)
                _safe_click(browser, add_btn)
                _wait_add_to_cart_feedback(browser, base_count, timeout=12)
                success = True
                break
            except TimeoutException as e2:
                errors.append(f"Товар {product_link_href} не добавился: {e2}")

    assert success, f"Не удалось добавить товар в корзину. Детали: {errors}"


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
