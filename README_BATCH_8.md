# Madarik Simplified User Journey — Batch 8

## Target branch

`feat/madarik-science-platform-v2`

## Scope

- Replace the split review-or-export result card with one review-and-export hub.
- Keep review available at all times.
- Block export visibly while required issues remain.
- Open the existing export workspace only after readiness is achieved.
- Show readiness and translation issue counts without exposing technical internals.
- Preserve all existing Backend, API, storage, review, and export callbacks.

## Changed files

- `frontend/src/features/workflow/QuickTranslationWorkspace.tsx`
- `frontend/src/features/workflow/ReviewExportDecision.tsx`
- `frontend/src/styles/simplified-platform.css`
- `backend/tests/test_simplified_user_journey_batch_2.py`
- `backend/tests/test_simplified_user_journey_batch_6.py`
- `backend/tests/test_simplified_user_journey_batch_8.py`

## Acceptance

GitHub Actions remains the final repository-wide gate for Backend pytest,
Frontend clean install, lint, TypeScript, and Vite production build.
