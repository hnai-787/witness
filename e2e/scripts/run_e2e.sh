#!/bin/bash
# Seed a disposable E2E database, start GuardSIS's Flask app, run the
# Selenium suite against it, then stop the app. Assumes GuardSIS
# (the secure student management system) lives as a sibling under
# projects/cybersecurity/ in this same workspace -- override via
# GUARDSIS_DIR if that's not the case.
set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARDSIS_DIR="${GUARDSIS_DIR:-$HERE/../../../cybersecurity/guardsis}"

export FLASK_ENV=development
export FLASK_DEBUG=0
export PORT="${PORT:-5050}"
export SECRET_KEY="${SECRET_KEY:-e2e-dev-secret-not-for-production-1234567890}"
export WTF_CSRF_SECRET_KEY="${WTF_CSRF_SECRET_KEY:-e2e-dev-csrf-secret-not-for-production-1234567890}"
export RATELIMIT_STORAGE_URI="${RATELIMIT_STORAGE_URI:-memory://}"
export BASE_URL="http://127.0.0.1:${PORT}"

echo "== seeding E2E database in $GUARDSIS_DIR =="
(cd "$GUARDSIS_DIR/src" && "$GUARDSIS_DIR/.venv/Scripts/python" seed_e2e.py)

echo "== starting GuardSIS app on $BASE_URL =="
(cd "$GUARDSIS_DIR/src" && "$GUARDSIS_DIR/.venv/Scripts/python" app.py > "$HERE/../results/app.log" 2>&1 &)

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
