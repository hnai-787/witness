from e2e_tests.pages.login_page import LoginPage


def test_valid_admin_login_reaches_dashboard(driver, base_url, admin_credentials):
    login = LoginPage.open(driver, base_url)
    dashboard = login.login(*admin_credentials)
    assert dashboard.student_rows()  # seeded students actually render
    assert "Dashboard" in dashboard.title


def test_valid_staff_login_reaches_dashboard(driver, base_url, staff_credentials):
    login = LoginPage.open(driver, base_url)
    dashboard = login.login(*staff_credentials)
    assert "Dashboard" in dashboard.title


def test_invalid_password_shows_generic_error(driver, base_url, admin_credentials):
    username, _ = admin_credentials
    login = LoginPage.open(driver, base_url)
    login.login_expecting_failure(username, "definitely-the-wrong-password")
    assert login.alerts.has_message_containing("Invalid username or password")


def test_unknown_username_shows_the_same_generic_error(driver, base_url):
    """Real browser confirmation of the anti-enumeration property Project
    #7's own pytest suite already checks at the HTTP layer: an unknown
    username and a wrong password must be visually indistinguishable.
    """
    login = LoginPage.open(driver, base_url)
    login.login_expecting_failure("no-such-user-at-all", "whatever12345")
    assert login.alerts.has_message_containing("Invalid username or password")


def test_logout_ends_the_session(driver, base_url, admin_dashboard):
    """Real bug found running this suite: clicking Logout submits a form
    (a real POST + redirect) asynchronously -- immediately issuing
    `driver.get(...)` right after `.click()` raced that in-flight
    navigation and sometimes won, leaving the test looking at the
    dashboard it never actually left. Waiting for the resulting login
    page to actually render (a real explicit-wait target, not a
    time.sleep) makes the two navigations happen in the right order.
    """
    admin_dashboard.navbar.click_logout()
    admin_dashboard.wait().until(lambda d: "Admin Login" in d.title)

    driver.get(f"{base_url}/dashboard")
    assert "Admin Login" in driver.title  # redirected to login, not showing the dashboard
