# Madarik Simplified User Journey — Batch 2

This batch continues the same branch `feat/madarik-science-platform-v2`.

## Scope

- Reduce the home screen after the three primary tasks.
- Collapse supporting tools under one optional drawer.
- Replace the post-processing action cluster with one decision:
  - review the remaining notes, or
  - export immediately when ready.
- Keep legacy compatibility labels and existing callbacks intact.
- Add regression tests for the simplified decision flow.

## Changed files

- `frontend/src/features/workflow/ScienceTaskHome.tsx`
- `frontend/src/features/workflow/QuickTranslationWorkspace.tsx`
- `frontend/src/styles/simplified-platform.css`
- `backend/tests/test_simplified_user_journey_batch_2.py`
