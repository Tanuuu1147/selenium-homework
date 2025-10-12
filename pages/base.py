# pages/base.py
import logging
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 10


class BasePage:
    def __init__(self, driver, base_url=None):
        self.driver = driver
        self.base_url = base_url
        logger.debug(f"Инициализация {self.__class__.__name__} с base_url: {base_url}")

    @allure.step("Открыть страницу: {url}")
    def open(self, url):
        logger.info(f"Открытие страницы: {url}")
        try:
            self.driver.get(url)
            logger.info(f"Страница успешно открыта: {url}")
        except Exception as e:
            logger.error(f"Ошибка при открытии страницы {url}: {str(e)}")
            raise
        return self

    @allure.step("Ожидание видимости элемента: {locator}")
    def wait_visible(self, locator, timeout=DEFAULT_TIMEOUT):
        logger.info(f"Ожидание видимости элемента: {locator}, таймаут: {timeout}с")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.info(f"Элемент стал видимым: {locator}")
            return element
        except Exception as e:
            logger.error(f"Элемент не стал видимым за {timeout}с: {locator}. Ошибка: {str(e)}")
            raise

    @allure.step("Ожидание кликабельности элемента: {locator}")
    def wait_clickable(self, locator, timeout=DEFAULT_TIMEOUT):
        logger.info(f"Ожидание кликабельности элемента: {locator}, таймаут: {timeout}с")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            logger.info(f"Элемент стал кликабельным: {locator}")
            return element
        except Exception as e:
            logger.error(f"Элемент не стал кликабельным за {timeout}с: {locator}. Ошибка: {str(e)}")
            raise

    @allure.step("Клик по элементу: {locator}")
    def click(self, locator, timeout=DEFAULT_TIMEOUT):
        logger.info(f"Клик по элементу: {locator}")
        el = self.wait_clickable(locator, timeout=timeout)
        try:
            el.click()
            logger.info(f"Успешный клик по элементу: {locator}")
        except Exception as e:
            logger.warning(f"Обычный клик не сработал для {locator}, пробуем JS клик. Ошибка: {str(e)}")
            # если Selenium не смог кликнуть — скроллим и жмём через JS
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)
            logger.info(f"Успешный JS клик по элементу: {locator}")

    @allure.step("Ввод текста '{text}' в элемент: {locator}")
    def type(self, locator, text, timeout=DEFAULT_TIMEOUT):
        logger.info(f"Ввод текста '{text}' в элемент: {locator}")
        try:
            el = self.wait_visible(locator, timeout=timeout)
            el.clear()
            el.send_keys(text)
            logger.info(f"Текст успешно введен в элемент: {locator}")
        except Exception as e:
            logger.error(f"Ошибка при вводе текста в элемент {locator}: {str(e)}")
            raise
