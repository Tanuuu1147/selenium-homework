import random
import re
import pytest

import logging


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException
from datetime import date, datetime
from selenium.webdriver.common.keys import Keys

# Настройка логгера для отладки
logger = logging.getLogger(__name__)


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

            except (StaleElementReferenceException, NoSuchElementException) as e:
                logger.warning(f"Failed to get text from cart indicator '{sel}': {e}")
            except WebDriverException as e:
                logger.error(f"WebDriver error getting cart indicator text: {e}")
            except Exception as e:
                logger.error(f"Unexpected error getting cart indicator text: {e}")

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
                    logger.debug("Element became stale while checking price symbol")
                    return False
            return False
        except StaleElementReferenceException:
            logger.debug("Elements became stale while finding prices")
            return False
        except (NoSuchElementException, WebDriverException) as e:
            logger.warning(f"Error finding price elements: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking price symbols: {e}")

            return False

    wait.until(_probe)





def _detect_product_type_and_requirements(driver):
    """
    Определяет тип товара на странице и возвращает информацию о требуемых полях.
    Возвращает словарь с типом товара и списком найденных обязательных полей.
    """
    product_info = {
        'product_name': 'Неизвестный товар',
        'product_url': driver.current_url,
        'required_fields': [],
        'product_type': 'standard'
    }
    
    # Получаем название товара для логирования
    try:
        name_element = driver.find_element(By.CSS_SELECTOR, "h1, .product-title, [data-oc-toggle='tooltip']:first-child")
        product_info['product_name'] = name_element.text.strip() or 'Неизвестный товар'
    except (NoSuchElementException, StaleElementReferenceException):
        logger.debug("Не удалось найти название товара")
    
    # Определяем якорные элементы для разных типов товаров
    anchor_elements = {
        'configurable': [
            '.form-group.required select',
            '.form-group.required input[type="radio"]',
            '.form-group.required input[type="checkbox"]'
        ],
        'custom_fields': [
            '.form-group.required input[type="text"]',
            '.form-group.required textarea'
        ],
        'date_time': [
            '.form-group.required input[type="date"]',
            '.form-group.required input[type="time"]',
            '.form-group.required input[type="datetime-local"]'
        ]
    }
    
    # Проверяем наличие различных типов полей
    for field_type, selectors in anchor_elements.items():
        found_elements = []
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                found_elements.extend([{selector: len(elements)}])
        
        if found_elements:
            product_info['required_fields'].append({
                'type': field_type,
                'elements': found_elements
            })
    
    # Определяем тип товара на основе найденных полей
    if any(field['type'] == 'configurable' for field in product_info['required_fields']):
        product_info['product_type'] = 'configurable'
    elif any(field['type'] == 'custom_fields' for field in product_info['required_fields']):
        product_info['product_type'] = 'custom'
    elif any(field['type'] == 'date_time' for field in product_info['required_fields']):
        product_info['product_type'] = 'booking'
    
    return product_info


def _fill_required_options_if_has_fields(driver):
    """
    Адаптивно заполняет обязательные поля в зависимости от типа товара.
    Логирует информацию о товаре и найденных полях для воспроизводимости.
    """
    product_info = _detect_product_type_and_requirements(driver)
    
    # Логируем информацию о товаре для отчета
    logger.info(f"Тестируемый товар: '{product_info['product_name']}'")
    logger.info(f"URL товара: {product_info['product_url']}")
    logger.info(f"Тип товара: {product_info['product_type']}")
    
    if not product_info['required_fields']:
        logger.info("На странице товара не найдено обязательных полей для заполнения")
        return
    
    # Логируем найденные обязательные поля
    for field_group in product_info['required_fields']:
        logger.info(f"Найдены обязательные поля типа '{field_group['type']}': {field_group['elements']}")
    
    # Заполняем поля в зависимости от типа
    for field_group in product_info['required_fields']:
        field_type = field_group['type']
        
        if field_type == 'configurable':
            _fill_configurable_options(driver)
        elif field_type == 'custom_fields':
            _fill_custom_text_fields(driver)
        elif field_type == 'date_time':
            _fill_date_time_fields(driver)


def _fill_configurable_options(driver):
    """Заполняет выпадающие списки, радиокнопки и чекбоксы."""

    # selects
    for sel in driver.find_elements(By.CSS_SELECTOR, ".form-group.required select"):
        try:
            s = Select(sel)

            for i, opt in enumerate(s.options):
                if (opt.get_attribute("value") or "").strip():
                    s.select_by_index(i)
                    logger.debug(f"Выбрана опция: {opt.text}")
                    break
        except (NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Не удалось выбрать опцию в выпадающем списке: {e}")
        except WebDriverException as e:
            logger.error(f"Ошибка WebDriver при выборе опции: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при выборе опции: {e}")


    # radios / checkboxes
    for css in (".form-group.required input[type='radio']",
                ".form-group.required input[type='checkbox']"):
        opts = driver.find_elements(By.CSS_SELECTOR, css)
        if opts:
            try:
                driver.execute_script("arguments[0].click();", opts[0])

                logger.debug(f"Выбрана опция: {css}")
            except (NoSuchElementException, StaleElementReferenceException) as e:
                logger.warning(f"Не удалось выбрать {css}: {e}")
            except WebDriverException as e:
                logger.error(f"Ошибка WebDriver при выборе {css}: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка при выборе {css}: {e}")


def _fill_custom_text_fields(driver):
    """Заполняет текстовые поля и текстовые области."""
    for css in (".form-group.required input[type='text']",
                ".form-group.required textarea"):
        for el in driver.find_elements(By.CSS_SELECTOR, css):
            try:
                el.clear()
                el.send_keys("Test")
                logger.debug(f"Заполнено текстовое поле: {css}")
            except (NoSuchElementException, StaleElementReferenceException) as e:
                logger.warning(f"Не удалось заполнить текстовое поле: {e}")
            except WebDriverException as e:
                logger.error(f"Ошибка WebDriver при заполнении текстового поля: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка при заполнении текстового поля: {e}")


def _fill_date_time_fields(driver):
    """Заполняет поля даты и времени."""
    # date
    today = date.today().strftime("%Y-%m-%d")
    for el in driver.find_elements(By.CSS_SELECTOR, ".form-group.required input[type='date']"):
        try:
            driver.execute_script("arguments[0].value = arguments[1];", el, today)
            el.send_keys(Keys.TAB)
            logger.debug(f"Установлена дата: {today}")
        except (NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Не удалось установить дату: {e}")
        except WebDriverException as e:
            logger.error(f"Ошибка WebDriver при установке даты: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при установке даты: {e}")

    # time
    noon = "12:00"
    for el in driver.find_elements(By.CSS_SELECTOR, ".form-group.required input[type='time']"):
        try:
            driver.execute_script("arguments[0].value = arguments[1];", el, noon)
            el.send_keys(Keys.TAB)
            logger.debug(f"Установлено время: {noon}")
        except (NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Не удалось установить время: {e}")
        except WebDriverException as e:
            logger.error(f"Ошибка WebDriver при установке времени: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при установке времени: {e}")

    # datetime-local
    dt = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")
    for el in driver.find_elements(By.CSS_SELECTOR, ".form-group.required input[type='datetime-local']"):
        try:
            driver.execute_script("arguments[0].value = arguments[1];", el, dt)
            el.send_keys(Keys.TAB)
            logger.debug(f"Установлена дата и время: {dt}")
        except (NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Не удалось установить дату и время: {e}")
        except WebDriverException as e:
            logger.error(f"Ошибка WebDriver при установке даты и времени: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при установке даты и времени: {e}")




from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def _wait_add_to_cart_feedback(driver, base_count: int, timeout: int = 12):
    """Ждём подтверждение: рост счётчика, alert-success или наличие строк в мини-корзине."""
    w = WebDriverWait(driver, timeout)
    
    def _ok(d):
        # Проверяем рост счетчика корзины
        try:
            current_count = _get_cart_count(d)
            if current_count > base_count:
                logger.debug(f"Cart count increased from {base_count} to {current_count}")
                return True
        except (NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Failed to get cart count: {e}")
        except WebDriverException as e:
            logger.error(f"WebDriver error while checking cart count: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while checking cart count: {e}")

        # Проверяем наличие уведомлений об успешном добавлении
        try:
            alerts = d.find_elements(By.CSS_SELECTOR, ".alert-success, #alert .alert-success, .toast")
            displayed_alerts = [a for a in alerts if a.is_displayed()]
            if displayed_alerts:
                logger.debug(f"Found {len(displayed_alerts)} success alert(s)")
                return True
        except (NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Failed to check success alerts: {e}")
        except WebDriverException as e:
            logger.error(f"WebDriver error while checking alerts: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while checking alerts: {e}")

        # Проверяем наличие товаров в мини-корзине
        try:
            btns = d.find_elements(By.CSS_SELECTOR, "#cart button, #header-cart button")
            if btns:
                d.execute_script("arguments[0].click();", btns[0])
                rows = d.find_elements(By.CSS_SELECTOR, "#cart .table tr, #header-cart .table tr")
                if rows:
                    logger.debug(f"Found {len(rows)} rows in cart dropdown")
                    return True
                else:
                    logger.debug("Cart dropdown opened but no items found")
        except (NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Failed to check cart dropdown: {e}")
        except WebDriverException as e:
            logger.error(f"WebDriver error while checking cart dropdown: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while checking cart dropdown: {e}")

        return False

    try:
        w.until(_ok)
    except TimeoutException:
        logger.error(f"Timeout waiting for cart feedback after {timeout} seconds. Base count was {base_count}")
        raise



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


    # Ждём появления главного меню админки - это самый надёжный индикатор успешного входа
    wait.until(EC.visibility_of_element_located((By.ID, "menu")))
    logger.debug("Успешно вошли в админ-панель - главное меню видимо")


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
                except (StaleElementReferenceException, NoSuchElementException) as e:
                    logger.warning(f"Failed to get href from element with selector '{sel}': {e}")
                except WebDriverException as e:
                    logger.error(f"WebDriver error getting href from element: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error getting href: {e}")
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
        _fill_required_options_if_has_fields(browser)

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
                _fill_required_options_if_has_fields(browser)
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
