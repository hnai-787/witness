"""Navbar component -- reused across dashboard/users/audit pages.

Uses `find_elements` (plural) throughout, never `find_element`: a
missing nav link is an expected, testable state (e.g. Staff has no
Users/Audit link) and should come back as an empty list, not raise
`NoSuchElementException`.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By


class Navbar:
    def __init__(self, driver):
        self.driver = driver

    def home_links(self):
        return self.driver.find_elements(By.ID, "nav-home")

    def audit_links(self):
        return self.driver.find_elements(By.ID, "nav-audit")

    def users_links(self):
        return self.driver.find_elements(By.ID, "nav-users")

    def logout_buttons(self):
        return self.driver.find_elements(By.ID, "nav-logout")

    def user_info_text(self) -> str | None:
        elements = self.driver.find_elements(By.ID, "nav-user-info")
        return elements[0].text if elements else None

    def click_logout(self) -> None:
        self.driver.find_element(By.ID, "nav-logout").click()

    def click_audit(self) -> None:
        self.driver.find_element(By.ID, "nav-audit").click()

    def click_users(self) -> None:
        self.driver.find_element(By.ID, "nav-users").click()
