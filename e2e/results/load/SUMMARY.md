# Load Test Summary

Real, measured results from four local Locust runs against Project #7
(`load/locustfile.py`, `AuthenticatedReadUser`: login once, then browse
/search/paginate `/dashboard`). One Flask dev-server process
(`memory://` rate-limit storage), fresh-restarted before each level so
every run starts from a clean rate-limiter state — see the exact
commands and environment in `../../PROJECT_NOTES.md`.

| Users | Spawn rate | Duration | Requests | Failures | Failure rate | Median | p95 | Requests/s |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1/s | 20s | 19 | 0 | 0.0% | 23 ms | 410 ms* | 1.05 |
| 5 | 2/s | 25s | 117 | 12 | 10.3% | 34 ms | 220 ms | 5.08 |
| 10 | 2/s | 30s | 262 | 217 | 82.8% | 17 ms | 66 ms | 9.78 |
| 20 | 4/s | 25s | 441 | 391 | 88.7% | 30 ms | 150 ms | 19.79 |

\* the 1-user p95 is skewed by a single slow `POST /login` (410ms) out
of only 19 total requests — not representative at that sample size.

## The finding

This is a real capacity characterization, not a flattering one, and it's
reported as found: Project #7's `default_limits=["100 per hour"]`
(app-wide, keyed per IP) saturates almost immediately once concurrent
traffic shares one IP address -- exactly what any NAT'd office network,
or this local experiment where all simulated users share `127.0.0.1`,
would produce. The failure rate jumps sharply between 5 users (10.3%)
and 10 users (82.8%): once the shared 100-requests-per-hour budget is
exhausted, essentially every subsequent request in that hour gets a 429
regardless of which user or route it's for.

This is not the same issue as the real GET-vs-POST `/login` rate-limit
bug found and fixed in Project #7 during this project's own test
development (see `../../PROJECT_NOTES.md`) — that was a key-function
bug causing an unintended limiter to apply to the wrong requests. This
is Project #7's own *deliberate* app-wide default, which is a reasonable
choice for a coursework security demonstration (aggressively resisting
abuse) but would need to be raised, scoped more precisely (e.g.
exempting authenticated read-only routes, or a per-user rather than
per-IP key for non-auth routes), or backed by a shared, larger-budget
store for any deployment expecting more than a handful of concurrent
users behind the same address.

## Environment

- OS: Windows 11, Flask dev server (`python app.py`), SQLite
- Python 3.12, Flask 3.1.3, Flask-Limiter 4.1.1, Locust 2.46.5
- `RATELIMIT_STORAGE_URI=memory://` (single process, in-memory -- see
  Project #7's own README for why this doesn't scale to multiple workers)
- Reproduce: `../scripts/run_e2e.sh` starts the app; then run the
  `locust` command from `../README.md` "Usage" at each user count.

This is a **controlled local concurrency characterization** on one
developer machine, not a production capacity or scalability claim.
