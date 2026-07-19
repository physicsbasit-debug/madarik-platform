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

require_command git
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
echo "=== Git whitespace check ==="
git diff --check

echo
echo "=== Repository release hygiene ==="
python - <<'PY'
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

root = Path.cwd()
tracked = subprocess.run(
    ["git", "ls-files"],
    cwd=root,
    check=True,
    text=True,
    stdout=subprocess.PIPE,
).stdout.splitlines()

forbidden: list[str] = []
secret_files: list[str] = []

for name in tracked:
    path = Path(name)
    parts = path.parts
    suffix = path.suffix.lower()
    basename = path.name

    if "__pycache__" in parts or suffix in {".pyc", ".pyo"}:
        forbidden.append(name)
    elif suffix in {".sqlite3", ".zip", ".patch"}:
        forbidden.append(name)
    elif name.startswith(
        (
            "backend/uploads/",
            "backend/temp/",
            "backend/exports/",
            "backend/generated/",
            "frontend/dist/",
            "frontend/node_modules/",
        )
    ):
        forbidden.append(name)

    if basename == ".env" or (
        basename.startswith(".env.") and basename != ".env.example"
    ):
        secret_files.append(name)
    elif suffix in {".pem", ".key"}:
        secret_files.append(name)

if forbidden:
    print("FAIL: generated or release-artifact files are tracked:")
    for item in forbidden:
        print(f"  - {item}")
    raise SystemExit(1)

if secret_files:
    print("FAIL: secret-bearing file types are tracked:")
    for item in secret_files:
        print(f"  - {item}")
    raise SystemExit(1)

binary_suffixes = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".docx",
    ".xlsx", ".zip", ".pyc", ".pyo", ".woff", ".woff2", ".ttf",
}
patterns = {
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}

findings: list[tuple[str, str]] = []
for name in tracked:
    path = root / name
    if not path.is_file() or path.suffix.lower() in binary_suffixes:
        continue
    try:
        if path.stat().st_size > 2_000_000:
            continue
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    for label, pattern in patterns.items():
        if pattern.search(text):
            findings.append((name, label))

if findings:
    print("FAIL: possible secret material detected:")
    for name, label in findings:
        print(f"  - {name}: {label}")
    raise SystemExit(1)

package = json.loads((root / "frontend/package.json").read_text(encoding="utf-8"))
frontend_version = str(package["version"])
readme = (root / "README.md").read_text(encoding="utf-8")
match = re.search(r"الإصدار البرمجي:\s*`([^`]+)`", readme)
if not match:
    raise SystemExit("FAIL: software version not found in README.md")

readme_version = match.group(1)
if frontend_version != readme_version:
    raise SystemExit(
        "FAIL: version mismatch: "
        f"frontend/package.json={frontend_version}, README.md={readme_version}"
    )

print(f"PASS: version is consistent: {frontend_version}")
print("PASS: no tracked generated artifacts, local secret files, or obvious keys.")
PY

echo
echo "=== Python syntax ==="
python -m compileall -q backend/app backend/tests

echo
echo "=== Backend dependency consistency ==="
python -m pip check

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
  npm config set registry https://registry.npmjs.org/
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

echo
echo "=== Final whitespace check ==="
git diff --check

if [[ "${RUN_LIVE_AI:-0}" == "1" ]]; then
  echo
  echo "=== Live external AI acceptance ==="
  python RUN_PHASE4_B1_LIVE_ACCEPTANCE.py
else
  echo
  echo "LIVE BLOCKER: external-provider Cambridge acceptance was not run."
  echo "Run with RUN_LIVE_AI=1 only after configuring a valid provider, model, and key."
fi

echo
echo "=== FINAL RC TECHNICAL GATE PASSED ==="
