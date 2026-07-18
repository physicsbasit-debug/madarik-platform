#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -x "$ROOT_DIR/backend/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/backend/.venv/bin/python"
else
  PYTHON_BIN="${PYTHON_BIN:-python}"
fi

echo "=== Python syntax ==="
"$PYTHON_BIN" -m py_compile \
  "$ROOT_DIR/backend/app/services/scientific_text.py" \
  "$ROOT_DIR/backend/app/services/export_review.py" \
  "$ROOT_DIR/backend/app/services/export.py" \
  "$ROOT_DIR/backend/app/services/full_exam_export.py" \
  "$ROOT_DIR/backend/app/services/readiness.py"

echo "=== Backend focused regression tests ==="
cd "$ROOT_DIR/backend"
"$PYTHON_BIN" -m pytest -q \
  tests/test_fix4_review_export_polish.py \
  tests/test_glossary_engine.py \
  tests/test_layout_asset_links.py \
  tests/test_layout_asset_link_api.py \
  tests/test_export_text_cleanup.py \
  tests/test_question_assets.py \
  tests/test_export_readiness.py \
  tests/test_docx_export.py \
  tests/test_pdf_export.py \
  tests/test_full_exam_export_acceptance.py \
  tests/test_full_exam_end_to_end_acceptance.py

echo "=== Frontend checks ==="
cd "$ROOT_DIR/frontend"
npm run lint
npm run build

echo "=== FIX 4 CHECKS PASSED ==="
