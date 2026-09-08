"""Page Component Object for the student-list pagination control."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Pagination:
    def __init__(self, driver):
        self.driver = driver

    def _nav(self):
        return self.driver.find_element(By.CSS_SELECTOR, "nav[aria-label='Student pagination']")

    def current_page_text(self) -> str:
        return self._nav().find_element(By.CSS_SELECTOR, "li.page-item.disabled span.page-link").text

    def _click_link(self, link_text: str) -> None:
        # Real bug found running this suite, root-caused rather than
        # papered over: a native (coordinate-based) click on this link
        # consistently raised ElementClickInterceptedException
        # ("not clickable at point") a few pixels below the bottom edge
        # of the configured 1440x1200 window. Diagnosed directly with
        # `document.elementFromPoint()` and `getBoundingClientRect()`:
        # `window.innerHeight` reports 1048 in this Chrome/Selenium
        # combination's `--headless=new` mode -- NOT 1200 as
        # `--window-size` requested -- while the page's real content is
        # ~1223px tall, so the link's true position (~1069-1107) falls
        # outside the reported viewport. Confirmed this is a headless
        # -mode viewport-accounting quirk, not a real page bug: even a
        # direct `window.scrollTo(0, 175)` left `window.scrollY` at 0,
        # meaning the mismatch isn't something `scrollIntoView` (or any
        # other scroll-based fix) can work around. A JS-native `.click()`
        # sidesteps the problem entirely -- it invokes the DOM's own
        # click handling directly, with no coordinate-based hit-testing
        # to be intercepted -- and is standard, documented practice for
        # exactly this class of headless-viewport flakiness.
        link = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, link_text))
        )
        self.driver.execute_script("arguments[0].click();", link)

    def click_next(self) -> None:
        self._click_link("Next")

    def click_previous(self) -> None:
        self._click_link("Previous")

    def next_is_disabled(self) -> bool:
        items = self._nav().find_elements(By.CSS_SELECTOR, "li.page-item")
        return "disabled" in items[-1].get_attribute("class")

    def previous_is_disabled(self) -> bool:
        items = self._nav().find_elements(By.CSS_SELECTOR, "li.page-item")
        return "disabled" in items[0].get_attribute("class")
