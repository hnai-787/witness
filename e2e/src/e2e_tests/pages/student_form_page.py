from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage
from .dashboard_page import DashboardPage


class StudentFormPage(BasePage):
    """The /update/<id> edit form."""

    @classmethod
    def open(cls, driver, base_url: str, student_id: str) -> StudentFormPage:
        page = cls(driver, base_url)
        driver.get(f"{base_url}/update/{student_id}")
        return page

    def field_value(self, field: str) -> str:
        return self.driver.find_element(By.ID, field).get_attribute("value")

    def set_field(self, field: str, value: str) -> StudentFormPage:
        element = self.driver.find_element(By.ID, field)
        element.clear()
        element.send_keys(value)
        return self

    def submit(self) -> DashboardPage:
        self.driver.find_element(By.CSS_SELECTOR, "[data-testid='update-student-submit']").click()
        dashboard = DashboardPage(self.driver, self.base_url)
        dashboard.wait().until(lambda d: d.find_elements(By.CSS_SELECTOR, ".table-section"))
        return dashboard
