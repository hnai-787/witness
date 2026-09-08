"""Base Page Object.

Selenium's own Page Object guidance (see README "Design decisions"):
Page Objects expose the SERVICES a page offers, not assertions -- tests
own the assertions. This base class therefore only provides navigation
and element-finding helpers; no `assert` statement appears anywhere
under `pages/` or `components/`.
"""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 5


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url

    def wait(self, timeout: float = DEFAULT_TIMEOUT) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    @property
    def title(self) -> str:
        return self.driver.title

    @property
    def current_url(self) -> str:
        return self.driver.current_url
