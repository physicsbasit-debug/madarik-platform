#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "FAIL: required command not found: $1" >&2
    exit 1
  fi
}

require_command python
require_command node
require_command npm

if [[ -f backend/.venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source backend/.venv/bin/activate
elif [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "=== Environment ==="
python --version
node --version
npm --version

echo
echo "=== Phase 10-B final RC preflight ==="
python RUN_PHASE10_B_RC_PREFLIGHT.py --repository-root .

echo
echo "=== Python syntax ==="
python -m compileall -q backend/app backend/tests

echo
echo "=== Backend dependency consistency ==="
python -m pip check

echo
echo "=== Phase 10-B focused acceptance ==="
PYTHONPATH=backend python -m pytest -q \
  backend/tests/test_phase10_a_release_readiness.py \
  backend/tests/test_phase10_a_end_to_end_acceptance.py \
  backend/tests/test_phase10_b_release_candidate.py

echo
echo "=== Backend full test suite ==="
(
  cd backend
  python -m pytest -q
)

echo
echo "=== Frontend clean dependency install ==="
(
  cd frontend
  if [[ "${SKIP_NPM_CI:-0}" == "1" ]]; then
    echo "SKIP_NPM_CI=1: using the existing node_modules directory."
  else
    npm ci --no-audit --no-fund
  fi

  echo
  echo "=== Frontend lint ==="
  npm run lint

  echo
  echo "=== Frontend production build ==="
  npm run build
)

if command -v git >/dev/null 2>&1 && [[ -d .git ]]; then
  echo
  echo "=== Final repository whitespace check ==="
  git diff --check
fi

if [[ "${RUN_LIVE_AI:-0}" == "1" ]]; then
  echo
  echo "=== Live external AI acceptance ==="
  python RUN_PHASE4_B1_LIVE_ACCEPTANCE.py
else
  echo
  echo "LIVE BLOCKER: external-provider Cambridge acceptance was not run."
  echo "Visual DOCX/PDF sign-off also remains required."
fi

echo
echo "=== PHASE 10-B TECHNICAL RC GATE PASSED ==="
