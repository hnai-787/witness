from __future__ import annotations

from selenium.webdriver.common.by import By

from ..components.alerts import Alerts
from .base_page import BasePage
from .dashboard_page import DashboardPage


class LoginPage(BasePage):
    @classmethod
    def open(cls, driver, base_url: str) -> LoginPage:
        page = cls(driver, base_url)
        driver.get(f"{base_url}/login")
        return page

    @property
    def alerts(self) -> Alerts:
        return Alerts(self.driver)

    def _username_field(self):
        return self.driver.find_element(By.ID, "username")

    def _password_field(self):
        return self.driver.find_element(By.ID, "password")

    def _submit_button(self):
        return self.driver.find_element(By.ID, "login-submit")

    def fill_credentials(self, username: str, password: str) -> LoginPage:
        self._username_field().clear()
        self._username_field().send_keys(username)
        self._password_field().clear()
        self._password_field().send_keys(password)
        return self

    def submit(self) -> None:
        self._submit_button().click()

    def login(self, username: str, password: str) -> DashboardPage:
        """Fill and submit the real login form, then wait for the
        dashboard's student table to actually render before returning --
        the caller shouldn't need to know how long that takes.
        """
        self.fill_credentials(username, password)
        self.submit()
        dashboard = DashboardPage(self.driver, self.base_url)
        dashboard.wait().until(lambda d: d.find_elements(By.CSS_SELECTOR, ".table-section"))
        return dashboard

    def login_expecting_failure(self, username: str, password: str) -> LoginPage:
        self.fill_credentials(username, password)
        self.submit()
        self.wait().until(lambda d: self.alerts.messages())
        return self
