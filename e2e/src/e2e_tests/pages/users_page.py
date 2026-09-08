from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from ..components.alerts import Alerts
from ..components.navbar import Navbar
from ..components.user_row import UserRow
from .base_page import BasePage


class UsersPage(BasePage):
    @classmethod
    def open(cls, driver, base_url: str) -> UsersPage:
        page = cls(driver, base_url)
        driver.get(f"{base_url}/users")
        return page

    @property
    def navbar(self) -> Navbar:
        return Navbar(self.driver)

    @property
    def alerts(self) -> Alerts:
        return Alerts(self.driver)

    def create_user(self, username: str, password: str, role: str) -> None:
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        Select(self.driver.find_element(By.ID, "role")).select_by_value(role)
        self.driver.find_element(By.CSS_SELECTOR, "[data-testid='create-user-submit']").click()
        self.wait().until(lambda d: self.alerts.messages())

    def user_rows(self) -> list[UserRow]:
        elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='user-row']")
        return [UserRow(e) for e in elements]

    def find_row_by_username(self, username: str) -> UserRow | None:
        for row in self.user_rows():
            if row.username == username:
                return row
        return None
