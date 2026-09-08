# Scripts

`run_e2e.sh` -- seeds a disposable E2E database in Project #7, starts its
Flask app, runs the Selenium suite against it. See the script itself for
the assumed sibling-directory layout and override variables.

`diagnose_pagination.py` -- the real diagnostic script used to root-cause
a genuine `ElementClickInterceptedException` on the pagination "Next"
link (a headless-Chrome viewport-accounting quirk, not a real app bug --
see `src/e2e_tests/components/pagination.py`'s docstring and
`PROJECT_NOTES.md` for the full story). Kept as evidence of how that bug
was actually diagnosed, not guessed at. Requires a running, seeded
Project #7 app at `http://127.0.0.1:5050`.
