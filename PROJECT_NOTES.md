# Project Notes

## Source

Migrated from `air-university-cybersecurity-projects/projects/software-testing-with-selenium`
into this workspace as an independent project on 2026-09-07.

## Cleanup decisions

None needed — no build output; no real credentials or actual AU-portal
screenshots are present (checked screenshots show only generic Selenium
IDE UI and Wikipedia).

## Assumptions / flags

- **Undocumented authorization**: this project load-tested Air
  University's real, live student-portal login page. No authorization from
  the university's IT department is referenced anywhere in the source
  report. Per an explicit decision made when reviewing this migration, an
  ethical-notice caveat was added to the README (rather than silently
  omitting it or hiding the project) and the project was kept public like
  the others rather than defaulted to private. If you have documentation
  of authorization for this testing, add it to the README; if not,
  consider this a flag for your own judgment about whether to keep this
  project public going forward.
- Group members listed are taken from the docx report's author list.

## Remaining work

- Confirm (or document) whether IT authorization existed for testing the
  live AU portal; update the Ethical Notice accordingly either way.

## 2026-09-09: Added e2e/ — a real Selenium suite retargeted at GuardSIS

### What changed and why

The original coursework load-tested a real, live third-party system (Air
University's student portal) with no documented authorization, and
captured no exported test scripts or quantitative results. The rebuild
retargets entirely at GuardSIS (the GuardSIS,
built earlier in this same session) -- a local app with no third-party
authorization question at all -- and builds a real, version-controlled
Selenium WebDriver + pytest suite (Page Object Model, Page Component
Objects, explicit waits, Selenium 4.48's built-in Selenium Manager)
covering login, CRUD, search, pagination, and role-specific UI behavior,
plus a separate Locust HTTP-level load experiment. Full research
grounding and design rationale is in `e2e/README.md`.

The original report/presentation/screenshots are untouched; only the new
`e2e/` directory was added.

### Six real bugs found and fixed getting this suite to 25/25

Every one of these was found by actually running the suite against a
live app and reading the real failure, not assumed away:

1. **A real bug in GuardSIS itself**: the per-account login rate
   limiter was unintentionally applying to plain GET requests (its key
   function falls back to the caller's IP when no username is present,
   true for every GET), turning a "5 login attempts per 5 minutes"
   control into an effective "5 page loads per 5 minutes" limit on the
   whole route. Fixed in GuardSIS's own `app.py`
   (`methods=["POST"]` added to that limiter), with a new regression
   test there. See GuardSIS's own `PROJECT_NOTES.md` for its side of
   this story.
2. **A CSRF-token regex that assumed attribute adjacency.** The
   HTTP-level session-setup helper (`_authenticate_via_http`) initially
   used `name="csrf_token" value="..."`, assuming those two attributes
   sit next to each other -- the real rendered tag is
   `id="csrf_token" name="csrf_token" type="hidden" value="..."`, so the
   regex never matched. Fixed to `name="csrf_token"[^>]*value="..."`
   (same fix applied to `load/locustfile.py`, which had the identical bug).
3. **A native browser `confirm()` dialog left unhandled.** Deleting a
   student triggers `onsubmit="return confirm(...)"` in GuardSIS's own
   markup; clicking Delete without accepting the resulting dialog left
   every subsequent WebDriver call raising
   `UnexpectedAlertPresentException`. Fixed in
   `components/student_row.py::click_delete` (`switch_to.alert.accept()`
   right after the click, since dismissing that dialog is part of
   *performing* the delete, not a separate assertion).
4. **A wait condition that was a no-op.** `DashboardPage.search()`
   originally waited for `.table-section` to exist after clicking
   Search -- but that element exists in both the pre- and post-search
   DOM, so the wait was satisfied instantly, before the browser had even
   started navigating. `student_rows()` then read the OLD, unfiltered
   page (a search for a literal `%` appeared to return all 12 students
   instead of zero, which looked at first like a real GuardSIS
   escaping regression -- it wasn't). Fixed with `EC.staleness_of()` on
   an element reference captured *before* the action, the standard
   idiomatic way to detect a real navigation actually happened. Applied
   to both `search()` and `sort_by_column()`.
5. **A real assumption bug in a test, not the app.**
   `test_admin_cannot_disable_their_own_account` read the admin's own
   username from `#nav-user-info` *after* already navigating to
   `/users` -- but that page's navbar (`users.html`) has no such element
   (only `dashboard.html`/`update.html` do), so it always returned
   `None`. The admin's username was already known from the credentials
   fixture; there was never a need to scrape it from the DOM.
6. **A race between a form submission and the next navigation.**
   `test_logout_ends_the_session` clicked Logout and immediately issued
   `driver.get(.../dashboard)` right after -- occasionally racing the
   in-flight logout POST/redirect and finding the dashboard still
   showing. Fixed by waiting for the resulting login page to actually
   render first.

### A genuine headless-Chrome viewport quirk, root-caused rather than papered over

The pagination "Next" link intermittently raised
`ElementClickInterceptedException` ("not clickable at point"), a few
pixels below the bottom edge of the configured 1440x1200 window. Adding
an `element_to_be_clickable` wait didn't fix it (that condition checks
`is_enabled()`, which is meaningless for a plain `<a>` -- it has no
native disabled state). Diagnosed directly rather than guessed at
(`scripts/diagnose_pagination.py`, kept as evidence): `window.innerHeight`
reports **1048**, not the requested 1200, in this Chrome/Selenium
combination's `--headless=new` mode, while the page's real content is
~1223px tall -- so the link's true position falls outside the reported
viewport. Confirmed this isn't fixable by scrolling: even a direct
`window.scrollTo(0, 175)` left `window.scrollY` at 0. The real fix is a
JS-native `.click()` (`components/pagination.py`), which invokes the
DOM's own click handling directly with no coordinate-based hit-testing
to intercept -- standard, documented practice for exactly this class of
headless-viewport flakiness, not a workaround-of-convenience.

### A real, honest capacity finding from the Locust load experiments

Four real local runs (1/5/10/20 simulated users, `AuthenticatedReadUser`:
login once, then browse/search/paginate) found that GuardSIS's
`default_limits=["100 per hour"]` (app-wide, per-IP) saturates almost
immediately once concurrent traffic shares one address: 0% failures at 1
user, 10.3% at 5, jumping to 82.8% at 10 and 88.7% at 20. This is a real
capacity characteristic of GuardSIS's current configuration, reported
as found rather than smoothed over -- see
`e2e/results/load/SUMMARY.md` for the full table and discussion, and note
that it's a *different* issue from the GET-vs-POST `/login` bug above
(that was a key-function bug misapplying one specific limiter; this is
GuardSIS's own deliberate but conservative app-wide default).

### Verification performed

All 25 tests pass against a real, live, freshly-seeded GuardSIS
instance (Chrome 152.0.7977.77, Selenium 4.48.0, headless) -- run
repeatedly while debugging real failures down to zero, not asserted from
a single lucky pass. Ruff reports zero issues. `pytest --collect-only`
(what CI actually runs -- see "CI limitation" below) passes cleanly. All
four Locust load levels were actually executed with fresh server
restarts between each for a clean rate-limiter baseline at every level.

### An honest CI limitation

This suite tests a separate, independent repository (GuardSIS), and
this workspace deliberately does not vendor project source as git
submodules. `.github/workflows/e2e-ci.yml` therefore validates linting
and test collection only -- real, meaningful checks that don't need a
live server -- rather than faking a live E2E run CI has no way to
actually perform for this multi-repo layout. See `e2e/README.md` "CI
limitation" for the full reasoning.

### Remaining work / honest limitations

See `e2e/README.md` "Limitations" -- notably: no per-test transactional
database rollback (tests use unique generated values to stay independent
instead), Chrome-only (no cross-browser matrix), and the forced-browsing
GET-only `/delete/<id>` check documents a real distinction (405 proves
the method is unavailable, not that a POST is denied) rather than
substituting for GuardSIS's own POST-as-Staff authorization test.
