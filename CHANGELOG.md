# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

### Changed

### Fixed

## [1.1.0] - 2026-09-09

### Added

- **`e2e/`**: a real, version-controlled Selenium WebDriver 4.48 + pytest
  suite retargeted at Project #7 (a local app this same effort built),
  replacing the original's untracked Selenium IDE recordings against a
  real, live third-party site. Page Object Model + Page Component
  Objects (`src/e2e_tests/pages/`, `components/`), explicit waits,
  Selenium Manager (no chromedriver checked in).
- 25 pytest tests (`tests/`): login/logout, student CRUD, search,
  pagination, role-specific UI (Staff vs. Admin), and forced-browsing /
  vertical-privilege-escalation checks (OWASP WSTG) confirming a
  privileged URL is rejected server-side even when the UI never offers it.
- `load/locustfile.py` and four real, committed local load-test runs
  (`results/load/`, 1/5/10/20 simulated users) with a written summary
  (`results/load/SUMMARY.md`) — genuine quantitative results, replacing
  the original's qualitative-only findings.
- `scripts/run_e2e.sh` (seed + start Project #7 + run the suite) and
  `scripts/diagnose_pagination.py` (the real diagnostic script that
  root-caused a headless-Chrome viewport quirk, kept as evidence).
- `.github/workflows/e2e-ci.yml`: Ruff + `pytest --collect-only`
  (documented honestly as a CI-scope limitation — see README).

### Changed

- `project.yaml`: `portfolio.featured` set to `true`.
- README's Ethical Notice: documented that this rebuild deliberately
  resolves the original's undocumented third-party-authorization gap by
  retargeting at a locally-owned app instead of repeating the pattern.

### Fixed

Six real bugs found and fixed while getting this suite to 25/25 (full
writeups in `PROJECT_NOTES.md`):

- A real bug in **Project #7 itself**: its per-account login rate
  limiter was unintentionally applying to plain GET requests, not just
  login attempts (fixed there, with a new regression test).
- A CSRF-token regex in this suite that assumed attribute adjacency
  (`name="..." value="..."`) when the real rendered tag has attributes
  in a different order.
- A native browser `confirm()` dialog left unhandled after clicking
  Delete, causing every subsequent WebDriver call to fail.
- A wait condition that was a no-op (`.table-section` exists both before
  and after a search), causing `search()`/`sort_by_column()` to
  occasionally read stale, pre-action page content.
- A test that scraped the admin's username from a DOM element that only
  exists on a different page than the one being read.
- A race between clicking Logout and immediately checking whether the
  session had actually ended.

Also root-caused (not merely worked around) a genuine headless-Chrome
viewport-accounting quirk causing intermittent
`ElementClickInterceptedException` on the pagination "Next" link — fixed
with a JS-native click, the standard remedy for this class of issue.
