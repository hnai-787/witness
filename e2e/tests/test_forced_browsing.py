"""Forced-browsing / vertical-privilege-escalation checks (OWASP WSTG
authorization testing category): a Staff user typing a privileged URL
directly must be rejected, not merely un-navigated-to via the UI.
"""

import pytest

from e2e_tests.pages.forbidden_page import ForbiddenPage


@pytest.mark.parametrize("path", ["/users", "/audit-log"])
def test_staff_cannot_force_browse_admin_pages(authenticated_staff_driver, base_url, path):
    authenticated_staff_driver.get(f"{base_url}{path}")
    forbidden = ForbiddenPage(authenticated_staff_driver, base_url)
    assert forbidden.status_code_text == "403"


@pytest.mark.parametrize("path", ["/dashboard", "/users", "/audit-log"])
def test_anonymous_cannot_force_browse_any_authenticated_page(driver, base_url, path):
    driver.get(f"{base_url}{path}")
    assert "Admin Login" in driver.title  # redirected to login, per @login_required


def test_staff_forced_delete_url_is_not_found_via_get_but_is_not_a_bypass(authenticated_staff_driver, base_url):
    """GET on a POST-only mutation route legitimately returns 405, which
    proves the GET method is unavailable -- NOT that Staff is denied the
    destructive POST. That stronger claim is Project #7's own pytest
    suite's job (a real POST as Staff -> 403). This test exists only to
    document that distinction, not to substitute for it.
    """
    authenticated_staff_driver.get(f"{base_url}/delete/1")
    assert "405" in authenticated_staff_driver.page_source or "Method Not Allowed" in authenticated_staff_driver.page_source
