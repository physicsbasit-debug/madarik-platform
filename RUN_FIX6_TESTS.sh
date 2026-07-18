#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON_BIN="$(command -v python)"
if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/backend/.venv/bin/python"
fi

echo "=== Python syntax ==="
"$PYTHON_BIN" -m py_compile \
  backend/app/models/project.py \
  backend/app/services/export_review.py \
  backend/app/services/export.py \
  backend/app/services/full_exam_export.py \
  backend/app/services/readiness.py \
  backend/app/services/session_store.py

echo "=== Backend focused regression tests ==="
cd backend
"$PYTHON_BIN" -m pytest -q \
  tests/test_fix6_marks_export_closure.py \
  tests/test_export_layout_polish.py \
  tests/test_fix4_review_export_polish.py \
  tests/test_fix5_scientific_snapshots.py \
  tests/test_full_exam_export_acceptance.py \
  tests/test_full_exam_end_to_end_acceptance.py \
  tests/test_docx_export.py \
  tests/test_pdf_export.py
cd "$ROOT"

echo "=== Frontend checks ==="
cd frontend
npm run lint
npm run build
cd "$ROOT"

echo "=== FIX 6 CHECKS PASSED ==="
