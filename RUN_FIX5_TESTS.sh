#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"

cd "$ROOT_DIR"

echo "=== Python syntax ==="
"$PYTHON_BIN" -m py_compile \
  backend/app/services/scientific_text.py \
  backend/app/services/export.py

echo "=== Backend focused regression tests ==="
cd backend
"$PYTHON_BIN" -m pytest -q \
  tests/test_fix5_scientific_snapshots.py \
  tests/test_fix4_review_export_polish.py \
  tests/test_export_text_cleanup.py \
  tests/test_docx_export.py \
  tests/test_pdf_export.py \
  tests/test_full_exam_export_acceptance.py

cd "$ROOT_DIR"

echo "=== Frontend checks ==="
cd frontend
npm run lint
npm run build

cd "$ROOT_DIR"
echo "=== FIX 5 CHECKS PASSED ==="
