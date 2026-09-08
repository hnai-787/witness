"""Page Component Object for one row of the student table."""

from __future__ import annotations

from selenium.webdriver.common.by import By


class StudentRow:
    def __init__(self, element):
        self.element = element

    @property
    def student_id(self) -> str:
        return self.element.get_attribute("data-student-id")

    def field(self, name: str) -> str:
        return self.element.find_element(By.CSS_SELECTOR, f"[data-field='{name}']").text

    @property
    def fname(self) -> str:
        return self.field("fname")

    @property
    def lname(self) -> str:
        return self.field("lname")

    @property
    def email(self) -> str:
        return self.field("email")

    @property
    def city(self) -> str:
        return self.field("city")

    def has_delete_action(self) -> bool:
        return bool(self.element.find_elements(By.CSS_SELECTOR, "[data-testid='delete-student']"))

    def has_edit_action(self) -> bool:
        return bool(self.element.find_elements(By.CSS_SELECTOR, "[data-testid='edit-student']"))

    def click_edit(self) -> None:
        self.element.find_element(By.CSS_SELECTOR, "[data-testid='edit-student']").click()

    def click_delete(self) -> None:
        """Click Delete and accept the resulting native browser confirm()
        dialog (dashboard.html's delete form uses
        `onsubmit="return confirm('Delete this student record?');"`).
        Real bug found running this suite: a bare `.click()` here raised
        UnexpectedAlertPresentException on the NEXT WebDriver call,
        because Selenium doesn't auto-dismiss native dialogs -- the
        driver just blocks until something explicitly switches to the
        alert and accepts or dismisses it.
        """
        self.element.find_element(By.CSS_SELECTOR, "[data-testid='delete-student']").click()
        self.element.parent.switch_to.alert.accept()
