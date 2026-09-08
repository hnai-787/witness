"""Page Component Object for one row of the Users admin table."""

from __future__ import annotations

from selenium.webdriver.common.by import By


class UserRow:
    def __init__(self, element):
        self.element = element

    @property
    def user_id(self) -> str:
        return self.element.get_attribute("data-user-id")

    @property
    def username(self) -> str:
        return self.element.find_element(By.CSS_SELECTOR, "[data-field='username']").text

    @property
    def role(self) -> str:
        return self.element.find_element(By.CSS_SELECTOR, "[data-field='role']").text

    def click_save_role(self) -> None:
        self.element.find_element(By.CSS_SELECTOR, "[data-testid='save-role']").click()

    def click_disable_toggle(self) -> None:
        self.element.find_element(By.CSS_SELECTOR, "[data-testid='disable-toggle']").click()

    def disable_toggle_is_disabled(self) -> bool:
        button = self.element.find_element(By.CSS_SELECTOR, "[data-testid='disable-toggle']")
        return not button.is_enabled()
