from __future__ import annotations

from selenium.webdriver.common.by import By

from ..components.navbar import Navbar
from .base_page import BasePage


class AuditPage(BasePage):
    @classmethod
    def open(cls, driver, base_url: str) -> AuditPage:
        page = cls(driver, base_url)
        driver.get(f"{base_url}/audit-log")
        return page

    @property
    def navbar(self) -> Navbar:
        return Navbar(self.driver)

    def entry_rows(self):
        table = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        return table

    def row_texts(self) -> list[str]:
        return [row.text for row in self.entry_rows()]
