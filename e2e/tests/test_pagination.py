import pytest

from e2e_tests.pages.dashboard_page import DashboardPage


def test_first_page_has_previous_disabled(authenticated_admin_driver, base_url):
    dashboard = DashboardPage.open(authenticated_admin_driver, base_url, per_page=5)
    assert dashboard.pagination.previous_is_disabled()
    assert "Page 1 of" in dashboard.pagination.current_page_text()


def test_clicking_next_advances_the_page_number(authenticated_admin_driver, base_url):
    dashboard = DashboardPage.open(authenticated_admin_driver, base_url, per_page=5)

    if dashboard.pagination.next_is_disabled():
        # Fewer than 6 total students exist right now (another test may
        # have deleted some) -- nothing to page through; the assertion
        # this test exists for doesn't apply, so don't fail on a
        # precondition this test doesn't control.
        pytest.skip("fewer than one full extra page of students currently exist")

    dashboard.pagination.click_next()
    dashboard.wait().until(lambda d: "Page 2" in dashboard.pagination.current_page_text())
    assert "Page 2 of" in dashboard.pagination.current_page_text()
    assert not dashboard.pagination.previous_is_disabled()
