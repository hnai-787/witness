#!/bin/bash
# Seed a disposable E2E database, start Rollkeeper's Flask app, run the
# Selenium suite against it, then stop the app. Assumes Rollkeeper
# (the secure student management system) lives as a sibling under
# projects/cybersecurity/ in this same workspace -- override via
# ROLLKEEPER_DIR if that's not the case.
set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROLLKEEPER_DIR="${ROLLKEEPER_DIR:-$HERE/../../../../cybersecurity/rollkeeper}"

export FLASK_ENV=development
export FLASK_DEBUG=0
export PORT="${PORT:-5050}"
export SECRET_KEY="${SECRET_KEY:-e2e-dev-secret-not-for-production-1234567890}"
export WTF_CSRF_SECRET_KEY="${WTF_CSRF_SECRET_KEY:-e2e-dev-csrf-secret-not-for-production-1234567890}"
export RATELIMIT_STORAGE_URI="${RATELIMIT_STORAGE_URI:-memory://}"
export BASE_URL="http://127.0.0.1:${PORT}"

echo "== seeding E2E database in $ROLLKEEPER_DIR =="
(cd "$ROLLKEEPER_DIR/src" && "$ROLLKEEPER_DIR/.venv/Scripts/python" seed_e2e.py)

echo "== starting Rollkeeper app on $BASE_URL =="
(cd "$ROLLKEEPER_DIR/src" && "$ROLLKEEPER_DIR/.venv/Scripts/python" app.py > "$HERE/../results/app.log" 2>&1 &)

echo "== waiting for the app to respond =="
for _ in $(seq 1 30); do
  if curl --fail --silent "$BASE_URL/" > /dev/null 2>&1; then
    echo "app is up"
    break
  fi
  sleep 1
done

echo "== running the Selenium suite =="
pytest -q "$HERE/.."

echo "== done (the Flask dev server process is left running; stop it manually or close the shell) =="
