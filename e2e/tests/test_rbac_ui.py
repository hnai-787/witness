"""Real-browser confirmation of Project #7's role-based UI.

Absence, not disabled: Project #7's intended contract is that Staff is
never OFFERED admin-only actions at all (see permissions.py), so these
assertions check that the controls are absent from the DOM
(`find_elements` returning an empty list), not merely disabled -- see
README "RBAC UI testing: absence vs. disabled".

Hidden UI is not authorization (OWASP): these tests only prove the
browser experience matches the intended security boundary. They do NOT
prove the boundary itself is enforced -- that's Project #7's own pytest
suite (server-side, via direct POST/GET requests bypassing the UI
entirely). See test_forced_browsing.py for the browser-level complement:
confirming Staff can't reach a privileged page even by typing its URL.
"""


def test_staff_navigation_omits_admin_features(staff_dashboard):
    nav = staff_dashboard.navbar
    assert nav.users_links() == []
    assert nav.audit_links() == []
    assert nav.home_links()  # non-privileged links are still present
    assert nav.logout_buttons()


def test_staff_student_rows_have_no_delete_action(staff_dashboard):
    rows = staff_dashboard.student_rows()
    assert rows  # sanity: there really are rows to check
    for row in rows:
        assert not row.has_delete_action()
        assert row.has_edit_action()  # staff DOES have edit -- only delete is admin-only


def test_admin_navigation_includes_admin_features(admin_dashboard):
    nav = admin_dashboard.navbar
    assert len(nav.users_links()) == 1
    assert len(nav.audit_links()) == 1


def test_admin_student_rows_have_delete_action(admin_dashboard):
    rows = admin_dashboard.student_rows()
    assert rows
    for row in rows:
        assert row.has_delete_action()


def test_admin_cannot_disable_their_own_account(authenticated_admin_driver, base_url, admin_credentials):
    """Real bug found running this suite: the original version of this
    test read the admin's username from `#nav-user-info` AFTER already
    navigating to /users -- but that page's navbar (users.html) has no
    such element (only dashboard.html/update.html do), so it always
    returned None. The admin's own username is already known (it's a
    fixture input), so there was never a need to scrape it from the DOM
    at all.
    """
    from e2e_tests.pages.users_page import UsersPage

    admin_username, _ = admin_credentials
    users = UsersPage.open(authenticated_admin_driver, base_url)
    own_row = users.find_row_by_username(admin_username)
    assert own_row is not None
    assert own_row.disable_toggle_is_disabled()
