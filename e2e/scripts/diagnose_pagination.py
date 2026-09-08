"""Real diagnostic script that root-caused a genuine pagination click bug.

Not part of the test suite -- kept as evidence of how
`ElementClickInterceptedException` on the "Next" pagination link was
actually diagnosed (see components/pagination.py's docstring and
PROJECT_NOTES.md), rather than fixed by guessing. Confirms:

- `window.innerHeight` reports 1048 in this Chrome/Selenium combination's
  `--headless=new` mode, not the 1200 requested via `--window-size`.
- The page's real content is taller than that (~1223px), so the link's
  true position falls outside the reported viewport.
- Even a direct `window.scrollTo(0, 175)` leaves `window.scrollY` at 0 --
  confirming this is a headless-mode viewport-accounting quirk that no
  scroll-based fix can work around, which is why the real fix
  (pagination.py) uses a JS-native click instead.

Requires a running Project #7 app seeded via seed_e2e.py (see
scripts/run_e2e.sh) at BASE_URL below.
"""

import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from e2e_tests.pages.dashboard_page import DashboardPage

BASE_URL = "http://127.0.0.1:5050"
_CSRF_RE = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


def main() -> None:
    session = requests.Session()
    login_page = session.get(f"{BASE_URL}/login")
    match = _CSRF_RE.search(login_page.text)
    session.post(
        f"{BASE_URL}/login",
        data={"username": "e2e_admin", "password": "E2eAdminPass12345!", "csrf_token": match.group(1)},
        allow_redirects=False,
    )
    cookie = session.cookies.get("session")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1200")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(BASE_URL)
        driver.add_cookie({"name": "session", "value": cookie, "path": "/"})
        DashboardPage.open(driver, BASE_URL, per_page=5)

        next_link = driver.find_element(By.LINK_TEXT, "Next")
        rect = driver.execute_script("return arguments[0].getBoundingClientRect();", next_link)
        print("Next link rect:", rect)
        print("window inner size:", driver.execute_script("return [window.innerWidth, window.innerHeight];"))

        driver.execute_script("window.scrollTo(0, 175);")
        print("scrollY after window.scrollTo(0, 175):", driver.execute_script("return window.scrollY;"))
        print("document.documentElement.scrollHeight:", driver.execute_script("return document.documentElement.scrollHeight;"))

        cx, cy = rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2
        elem_at_center = driver.execute_script(f"return document.elementFromPoint({cx}, {cy});")
        print("elementFromPoint(link center):", driver.execute_script(
            "return arguments[0] ? arguments[0].outerHTML : null;", elem_at_center
        ))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
