"""Page Component Object for the flash-message alert area."""

from __future__ import annotations

from selenium.webdriver.common.by import By


class Alerts:
    def __init__(self, driver):
        self.driver = driver

    def messages(self) -> list[str]:
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert")
        return [e.text for e in elements]

    def has_message_containing(self, text: str) -> bool:
        return any(text in message for message in self.messages())
