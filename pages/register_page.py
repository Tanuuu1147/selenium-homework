from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base import BasePage

class RegisterPage(BasePage):
    FIRSTNAME = (By.CSS_SELECTOR, "#input-firstname")
    LASTNAME  = (By.CSS_SELECTOR, "#input-lastname")
    EMAIL     = (By.CSS_SELECTOR, "#input-email")
    TELEPHONE = (By.CSS_SELECTOR, "#input-telephone")
    PASSWORD  = (By.CSS_SELECTOR, "#input-password")

    AGREE     = (By.NAME, "agree")
    AGREE_LABEL = (By.CSS_SELECTOR, "label[for='input-agree'], label[for='agree'], #agree + label")
    SUBMIT    = (By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
    SUCCESS_HEADING = (By.CSS_SELECTOR, "#content h1")

    def open_register(self, base_url):
        return self.open(base_url + "/index.php?route=account/register")

    def _type_if_present(self, locator, text) -> bool:
        els = self.driver.find_elements(*locator)
        if els:
            el = els[0]
            el.clear()
            el.send_keys(text)
            return True
        return False

    def _type_confirm_password(self, password: str):

        for locator in [(By.CSS_SELECTOR, "#input-confirm"), (By.NAME, "confirm")]:
            if self._type_if_present(locator, password):
                return

        pw_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if len(pw_fields) >= 2:
            try:
                el = pw_fields[1]
                el.clear()
                el.send_keys(password)
                return
            except Exception:
                pass


    def _ensure_agree_checked(self):

        inputs = self.driver.find_elements(*self.AGREE)
        if inputs:
            agree = inputs[0]
            if not agree.is_selected():
                try:
                    self.click(self.AGREE)
                except Exception:
                    pass
            if not agree.is_selected():

                labels = self.driver.find_elements(*self.AGREE_LABEL)
                if labels:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", labels[0])
                    self.driver.execute_script("arguments[0].click();", labels[0])

    def _wait_success_or_errors(self, timeout: int = 8):
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(lambda d: "success" in (d.current_url or "").lower()
                                 or "Your Account Has Been Created" in (d.title or "")
                                 or "Your Account Has Been Created" in (d.find_element(*self.SUCCESS_HEADING).text or ""))
            return True
        except Exception:
            return False

    def register(self, firstname, lastname, email, password):
        self.type(self.FIRSTNAME, firstname)
        self.type(self.LASTNAME,  lastname)
        self.type(self.EMAIL,     email)
        self._type_if_present(self.TELEPHONE, "0123456789")
        self.type(self.PASSWORD,  password)
        self._type_confirm_password(password)
        self._ensure_agree_checked()
        self.click(self.SUBMIT)

        if self._wait_success_or_errors(timeout=10):
            return WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.SUCCESS_HEADING))


        error_selectors = [
            ".text-danger", ".invalid-feedback", ".alert-danger", ".alert-warning"
        ]
        messages = []
        for css in error_selectors:
            for el in self.driver.find_elements(By.CSS_SELECTOR, css):
                txt = (el.text or "").strip()
                if txt:
                    messages.append(txt)
        msg = "; ".join(messages)
        raise AssertionError(f"Регистрация не завершилась успехом. Заголовок='{(self.driver.find_element(*self.SUCCESS_HEADING).text if self.driver.find_elements(*self.SUCCESS_HEADING) else 'N/A')}'. Ошибки: {msg or 'не найдены'}")
