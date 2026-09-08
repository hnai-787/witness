import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
import requests
from selenium import webdriver

from e2e_tests.pages.dashboard_page import DashboardPage

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5050")
HEADLESS = os.environ.get("HEADLESS", "1") == "1"

ADMIN_USERNAME = os.environ.get("E2E_ADMIN_USERNAME", "e2e_admin")
ADMIN_PASSWORD = os.environ.get("E2E_ADMIN_PASSWORD", "E2eAdminPass12345!")
STAFF_USERNAME = os.environ.get("E2E_STAFF_USERNAME", "e2e_staff")
STAFF_PASSWORD = os.environ.get("E2E_STAFF_PASSWORD", "E2eStaffPass12345!")

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "results" / "artifacts"

# Deliberately NOT assuming attribute order or adjacency -- a real bug
# found while first running this suite: the actual rendered tag is
# `<input id="csrf_token" name="csrf_token" type="hidden" value="...">`,
# so a regex requiring `name="csrf_token" value="..."` to be adjacent
# never matched. `[^>]*` matches any attributes in between without
# crossing the tag boundary.
_CSRF_RE = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def admin_credentials() -> tuple[str, str]:
    return ADMIN_USERNAME, ADMIN_PASSWORD


@pytest.fixture
def staff_credentials() -> tuple[str, str]:
    return STAFF_USERNAME, STAFF_PASSWORD


@pytest.fixture
def driver():
    """A fresh WebDriver instance per test -- new browser, new profile,
    new cookies, new session state (Selenium's own recommendation, and
    essential here since the same suite exercises anonymous/staff/admin
    identities and must never leak session state between them). Uses
    Selenium Manager (built into Selenium 4.6+) for driver discovery --
    no chromedriver binary is downloaded or checked into this repo.
    """
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1200")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


def _authenticate_via_http(username: str, password: str) -> str:
    """Perform ONE real login over plain HTTP (not through the browser)
    and return the resulting Flask session cookie value.

    Why: a real bug found while first running this suite -- every test
    doing its own full browser-driven login form submission collectively
    exceeded Project #7's own real rate limiter (20/min per IP, 5/5min
    per account) within the first dozen tests, since they all share one
    machine's IP and the same two seeded accounts. Project #7's own
    research explicitly sanctions this pattern: "establishing a session
    through a safe test helper" is a defensible way to set up
    prerequisite state, reserving actual browser-driven login submission
    for the tests that are specifically ABOUT the login form itself
    (test_login.py, which stays exactly as written).
    """
    session = requests.Session()
    login_page = session.get(f"{BASE_URL}/login", timeout=10)
    match = _CSRF_RE.search(login_page.text)
    if not match:
        raise RuntimeError("could not find a CSRF token on the login page -- is BASE_URL correct?")

    response = session.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": password, "csrf_token": match.group(1)},
        timeout=10,
        allow_redirects=False,
    )
    if response.status_code not in (302, 303):
        raise RuntimeError(f"HTTP login for {username!r} did not redirect (got {response.status_code}) -- bad credentials or a real login-flow regression")

    cookie = session.cookies.get("session")
    if not cookie:
        raise RuntimeError("login appeared to succeed but no 'session' cookie was set")
    return cookie


def _inject_session(driver, cookie_value: str) -> None:
    driver.get(BASE_URL)  # must be on the target domain before add_cookie works
    driver.delete_all_cookies()
    driver.add_cookie({"name": "session", "value": cookie_value, "path": "/"})


@pytest.fixture(scope="session")
def _admin_session_cookie() -> str:
    return _authenticate_via_http(ADMIN_USERNAME, ADMIN_PASSWORD)


@pytest.fixture(scope="session")
def _staff_session_cookie() -> str:
    return _authenticate_via_http(STAFF_USERNAME, STAFF_PASSWORD)


@pytest.fixture
def admin_dashboard(driver, base_url, _admin_session_cookie) -> DashboardPage:
    _inject_session(driver, _admin_session_cookie)
    return DashboardPage.open(driver, base_url)


@pytest.fixture
def staff_dashboard(driver, base_url, _staff_session_cookie) -> DashboardPage:
    _inject_session(driver, _staff_session_cookie)
    return DashboardPage.open(driver, base_url)


@pytest.fixture
def authenticated_admin_driver(driver, _admin_session_cookie):
    """For tests that need the raw driver already logged in as admin but
    don't want a DashboardPage (e.g. navigating straight to /users).
    """
    _inject_session(driver, _admin_session_cookie)
    return driver


@pytest.fixture
def authenticated_staff_driver(driver, _staff_session_cookie):
    _inject_session(driver, _staff_session_cookie)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On failure, save a screenshot and the page HTML under
    results/artifacts/<test-name>/ -- a `NoSuchElementException` with no
    visual context is much harder to debug than one with a screenshot.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    test_dir = ARTIFACTS_DIR / item.name
    test_dir.mkdir(parents=True, exist_ok=True)

    try:
        driver.save_screenshot(str(test_dir / "screenshot.png"))
        (test_dir / "page.html").write_text(driver.page_source, encoding="utf-8")
        (test_dir / "url.txt").write_text(driver.current_url, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 -- best-effort diagnostics, must never mask the real failure
        (test_dir / "artifact_capture_error.txt").write_text(str(exc), encoding="utf-8")
