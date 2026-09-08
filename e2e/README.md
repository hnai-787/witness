# FlowCheck — real browser verification for GuardSIS

A version-controlled Selenium WebDriver + pytest suite that exercises
the actual rendered browser experience of GuardSIS (the Secure
Student Management System): login, CRUD, search, pagination, and —
the part that's genuinely complementary to GuardSIS's own pytest
suite — confirming in a **real browser** that a Staff account's UI
actually hides Delete/Users/Audit-Log controls, and that direct URL
access to those pages is still rejected server-side even when the UI
never offers them.

```text
GuardSIS Flask application (a separate, independent repo)
        |
        +-- pytest / Flask test client -------- backend/security verification (GuardSIS's own suite)
        |
        +-- live HTTP server
                |
                v
          Selenium WebDriver (Selenium 4.48, Selenium Manager -- no chromedriver checked in)
                |
          Page Object + Page Component layer
                |
                v
          browser workflows / RBAC UI verification
                |
                v
             pytest results

Separate: Locust HttpUser -> local Flask endpoints -> RPS / failures / median / p95 / p99
```

## Why this project changed targets

The original coursework load-tested Air University's real, live
student-portal login page and Wikipedia's search, without documented
authorization for the former, and captured no quantitative results. The
rebuilt suite targets a locally controlled application (GuardSIS,
which this same effort built) instead, and separates browser functional
testing from controlled HTTP-level performance measurement. See
`../PROJECT_NOTES.md`.

## Usage

```bash
pip install -e ".[dev]"

# start GuardSIS (see scripts/run_e2e.sh for the full seed+start+run flow)
BASE_URL=http://127.0.0.1:5050 HEADLESS=1 pytest -q

# real HTTP-level concurrency characterization (see "Load testing" below)
pip install -e ".[load]"
locust -f load/locustfile.py --headless --users 10 --spawn-rate 2 --run-time 30s \
  --host http://127.0.0.1:5050 --csv results/load/local-10users --html results/load/local-10users.html
```

## Design decisions worth knowing

- **Page Objects expose services, tests own the assertions** (Selenium's
  own current guidance): no `assert` statement exists anywhere under
  `src/e2e_tests/pages/` or `components/`. A Page Object only knows how
  the UI is structured; the test describes the expected behavior.
- **Page Component Objects** (`components/navbar.py`, `student_row.py`,
  `user_row.py`, `pagination.py`, `alerts.py`) for the pieces that repeat
  across pages, rather than duplicating locators in every Page Object.
- **`find_elements` (plural), never `find_element`, for anything that
  might legitimately be absent** — a missing Delete button for a Staff
  user is an expected, testable state (an empty list), not an exception.
- **Absence, not disabled, for forbidden UI** — GuardSIS's intended
  contract is that Staff is never *offered* admin-only actions, so tests
  assert `[] == controls`, matching that contract. See
  `test_rbac_ui.py`.
- **Hidden UI is not authorization** (OWASP). Every RBAC-UI test has a
  forced-browsing counterpart (`test_forced_browsing.py`) that requests
  the privileged URL directly, bypassing the UI entirely — proving the
  *server* rejects it, not just that the browser experience hides it.
- **Selenium Manager, not a checked-in chromedriver** — Selenium 4.6+
  ships its own driver manager; `webdriver.Chrome(options=options)` is
  the whole setup.
- **HTTP-level session establishment for non-login tests** (see "A real
  rate-limiting interaction" below) — real browser-driven login is
  reserved for `test_login.py`, which is specifically about the login
  form.
- **Locust, not more Selenium, for load** — Selenium's own documentation
  places performance testing in its discouraged-practices list (browser
  startup/rendering/instrumentation overhead makes it impossible to
  distinguish application performance from automation noise). Locust's
  `HttpUser` models real authenticated sessions (cookies included)
  without that overhead.

## A real rate-limiting interaction found while building this

The first full run of this suite failed almost everywhere with
`NoSuchElementException` on the login form. The actual cause, found by
reading the raw HTTP response rather than guessing: every test doing its
own full browser-driven login submission collectively exceeded Project
#7's real rate limiter within the first dozen tests — worse, `curl -sI
.../login` showed `X-RateLimit-Limit: 5` on a **bare GET request**,
meaning GuardSIS's per-account limiter (5 attempts per 5 minutes,
meant for repeated login *attempts*) was silently also counting every
plain page load, because its key function falls back to the caller's IP
when no username is present in the request — true for every GET. That
turned a "5 attempts per 5 minutes" login-abuse control into an
effective "5 page loads per 5 minutes" limit on the whole IP.

**Fixed in GuardSIS itself** (`app.py`, `@limiter.limit(..., key_func=
_account_rate_limit_key, methods=["POST"])`), with a new regression test
in GuardSIS's own suite (`test_repeated_get_requests_to_login_do_not_
trip_the_account_limiter`). This suite's non-login tests now establish
their session via one real HTTP login per role (`requests`, not
Selenium) instead of a fresh browser-driven login per test — both
changes were needed; either alone would have left the other route to the
same failure mode. See `../PROJECT_NOTES.md` for the full investigation,
including the multiple false leads ruled out along the way (stale
background server processes, a CSRF-token regex that assumed attribute
adjacency) before the real cause was found.

## Verification performed

All 25 tests pass against a real, live, freshly-seeded GuardSIS
instance (`HEADLESS=1`, Chrome 152, Selenium 4.48.0 via Selenium
Manager) — not asserted, actually run, repeatedly, while debugging real
failures down to zero. Ruff reports zero issues. `pytest --collect-only`
(what CI actually runs, see "CI limitation" below) passes cleanly.

## CI limitation (an honest one)

This suite tests a **separate, independent git repository** (Project
#7), and this workspace deliberately does not vendor project source as
git submodules (see the root `CLAUDE.md`). A real GitHub Actions run for
*this* repo has no way to check out that sibling repo without one, so
`.github/workflows/e2e-ci.yml` validates what it actually can in
isolation — linting and test collection (import/fixture sanity, catches
real breakage without needing a live server) — and documents, rather
than fakes, that full live execution and the Locust load experiments
are local-only. This mirrors how the research this suite was built from
already treats performance measurement: a documented local run, not a
CI regression gate.

## Load testing

See `results/load/` for four real, committed runs (1, 5, 10, and 20
simulated users, 20-30s each, `memory://` rate-limit storage, one
Flask dev-server process) and `PROJECT_NOTES.md` for the full write-up
of what they found — including a genuine capacity finding (GuardSIS's
current `default_limits=["100 per hour"]` saturates almost immediately
under any real concurrent traffic sharing one IP, which is exactly what
this kind of local experiment exists to reveal). These are a
**controlled local concurrency characterization**, not a production
scalability claim — see `load/locustfile.py`'s docstring.

## Limitations

- Tests against GuardSIS do not share a per-test transactional
  rollback (GuardSIS has no such mechanism) — the E2E database is
  seeded once via `seed_e2e.py` before a run, and tests that create data
  use unique values (UUID-suffixed emails) to stay independent of each
  other's side effects rather than requiring per-test isolation the
  underlying app doesn't support.
- No cross-browser matrix (Chrome only) — Firefox/Edge would need their
  own driver-availability verification this session didn't do.
- The forced-browsing GET-only `/delete/<id>` check documents a real
  distinction (405 proves the method is unavailable, not that a POST is
  denied) rather than substituting for GuardSIS's own POST-as-Staff
  test, which is what actually proves the authorization boundary.

## Future Enhancements

- A dedicated E2E database per CI run with a real sibling-repo checkout
  strategy, if this workspace's multi-repo model is ever revisited.
- Firefox/Edge cross-browser execution.
- A Locust scenario exercising the admin-only routes under load, kept
  separate from the read-heavy staff workload here.
