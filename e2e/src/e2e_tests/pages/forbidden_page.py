from __future__ import annotations

from .base_page import BasePage


class ForbiddenPage(BasePage):
    """Not navigated to directly -- represents wherever the driver
    currently is after a forced-browsing attempt, so the test can assert
    on the resulting error page without a page-specific `.open()`.
    """

    @property
    def status_code_text(self) -> str:
        """The numeric status code as shown in the page title
        (error.html renders "Error {{ code }} - ..."), independent of
        the surrounding wording.
        """
        for word in self.title.split():
            if word.isdigit():
                return word
        return ""
