from __future__ import annotations

from urllib.parse import urlencode

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..components.alerts import Alerts
from ..components.navbar import Navbar
from ..components.pagination import Pagination
from ..components.student_row import StudentRow
from .base_page import BasePage


class DashboardPage(BasePage):
    @classmethod
    def open(cls, driver, base_url: str, **query) -> DashboardPage:
        page = cls(driver, base_url)
        url = f"{base_url}/dashboard"
        if query:
            url += "?" + urlencode(query)
        driver.get(url)
        return page

    @property
    def navbar(self) -> Navbar:
        return Navbar(self.driver)

    @property
    def alerts(self) -> Alerts:
        return Alerts(self.driver)

    @property
    def pagination(self) -> Pagination:
        return Pagination(self.driver)

    def has_add_student_form(self) -> bool:
        return bool(self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='add-student-submit']"))

    def add_student(self, fname: str, lname: str, age: int, city: str, email: str) -> None:
        self.driver.find_element(By.ID, "fname").send_keys(fname)
        self.driver.find_element(By.ID, "lname").send_keys(lname)
        self.driver.find_element(By.ID, "age").send_keys(str(age))
        self.driver.find_element(By.ID, "city").send_keys(city)
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.CSS_SELECTOR, "[data-testid='add-student-submit']").click()
        self.wait().until(lambda d: self.alerts.messages())

    def student_rows(self) -> list[StudentRow]:
        elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='student-row']")
        return [StudentRow(e) for e in elements]

    def find_row_by_email(self, email: str) -> StudentRow | None:
        for row in self.student_rows():
            if row.email == email:
                return row
        return None

    def _wait_for_reload(self, marker) -> None:
        """Wait for a real page reload following a form submission or
        link click, given a WebElement reference captured BEFORE the
        action.

        Real bug found running this suite: waiting for
        `d.find_elements(By.CSS_SELECTOR, ".table-section")` after a
        search submission is a no-op -- that section exists in BOTH the
        pre-search and post-search DOM, so the condition is already true
        at the instant of the click, before the browser has even started
        navigating to the new URL. `student_rows()` then read the OLD,
        unfiltered page. `EC.staleness_of` on an element reference
        captured before the action is the correct, standard way to
        detect that a real navigation actually happened.
        """
        WebDriverWait(self.driver, 5).until(EC.staleness_of(marker))

    def search(self, query: str) -> None:
        marker = self.driver.find_element(By.CSS_SELECTOR, ".table-section")
        field = self.driver.find_element(By.ID, "search-input")
        field.clear()
        field.send_keys(query)
        self.driver.find_element(By.ID, "search-submit").click()
        self._wait_for_reload(marker)

    def sort_by_column(self, label: str) -> None:
        # PARTIAL_LINK_TEXT, not LINK_TEXT: an actively-sorted column's
        # link text has a trailing arrow indicator (see dashboard.html),
        # which would break an exact-match lookup once that column is
        # already the active sort.
        marker = self.driver.find_element(By.CSS_SELECTOR, ".table-section")
        self.driver.find_element(By.PARTIAL_LINK_TEXT, label).click()
        self._wait_for_reload(marker)
