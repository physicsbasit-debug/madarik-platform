#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -f backend/.venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source backend/.venv/bin/activate
elif [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "=== Python syntax ==="
python -m py_compile \
  backend/app/models/project.py \
  backend/app/services/ai_provider.py \
  backend/app/services/full_exam_translation.py \
  backend/tests/test_phase4_b1_real_ai_translation_acceptance.py

echo "=== Backend focused acceptance tests ==="
cd backend
python -m pytest -q \
  tests/test_phase4_b1_real_ai_translation_acceptance.py \
  tests/test_ai_provider_layer.py \
  tests/test_full_exam_translation_acceptance.py \
  tests/test_translation_batch_reliability.py
cd ..

echo "=== Frontend checks ==="
cd frontend
npm run lint
npm run build
cd ..

echo "=== PHASE 4-B1 CHECKS PASSED ==="
