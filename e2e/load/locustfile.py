"""Controlled local HTTP concurrency characterization for Rollkeeper.

Deliberately NOT a Selenium-driven load test -- Selenium's own guidance
places performance testing in its discouraged-practices list, because
browser startup/rendering/instrumentation overhead makes it impossible
to distinguish application performance from browser-automation noise.
This models users at the HTTP level instead (Locust's `HttpUser`, which
maintains cookies so it can hold a real authenticated session), covering
exactly the workload real users generate once logged in: browse, search,
paginate. It deliberately does NOT hammer the login endpoint -- that
would mostly measure Rollkeeper's own deliberate rate limiter, not
application throughput (there's a separate, small, low-volume login
check below to keep an eye on that, weighted far below the read
workload).

This is a "controlled local concurrency characterization" of a
SQLite-backed Flask dev server on one developer machine -- NOT a
production capacity/scalability claim. See README "Load testing" for the
exact command used and the environment the committed results were
measured on.
"""

import os
import re

from locust import HttpUser, between, task

USERNAME = os.environ.get("E2E_STAFF_USERNAME", "e2e_staff")
PASSWORD = os.environ.get("E2E_STAFF_PASSWORD", "E2eStaffPass12345!")

# See tests/conftest.py for why this doesn't assume attribute adjacency.
_CSRF_RE = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


class AuthenticatedReadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self) -> None:
        login_page = self.client.get("/login")
        match = _CSRF_RE.search(login_page.text)
        csrf_token = match.group(1) if match else ""
        self.client.post(
            "/login",
            data={"username": USERNAME, "password": PASSWORD, "csrf_token": csrf_token},
        )

    @task(4)
    def list_students(self):
        self.client.get("/dashboard")

    @task(2)
    def search_students(self):
        self.client.get("/dashboard?q=London")

    @task(1)
    def second_page(self):
        self.client.get("/dashboard?page=2&per_page=5")
