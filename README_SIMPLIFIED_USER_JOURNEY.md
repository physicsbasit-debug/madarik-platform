# Madarik Simplified User Journey UI

Target repository: `physicsbasit-debug/madarik-platform`  
Target branch: `feat/madarik-science-platform-v2`

## Scope

This package is the first implementation batch for replacing the old platform shell with a task-first user journey.

### Changed

- Removed the persistent grouped sidebar from `PlatformShell`.
- Reduced primary navigation to: Home, My Work, Question Bank.
- Rebuilt the home screen around three primary tasks:
  - Process an existing exam paper.
  - Create a new assessment.
  - Create a differentiated activity.
- Added device, Google Drive, and OneDrive source choices at the point of file selection.
- Rebuilt quick paper processing into three visible steps:
  - Upload.
  - Prepare automatically.
  - Review issues or export.
- Hid optional paper metadata inside progressive disclosure.
- Preserved the existing callbacks, section keys, data types, backend contracts, and current processing engine.
- Added a scoped responsive CSS layer and structural regression tests.

## Files

- `frontend/src/components/PlatformShell.tsx`
- `frontend/src/features/workflow/ScienceTaskHome.tsx`
- `frontend/src/features/workflow/QuickTranslationWorkspace.tsx`
- `frontend/src/styles/simplified-platform.css`
- `backend/tests/test_simplified_user_journey_ui.py`

## Validation completed in the isolated harness

- TypeScript strict mode: passed.
- `noUnusedLocals`: passed.
- `noUnusedParameters`: passed.
- CSS brace integrity: passed.
- Component callback contracts matched against the current public branch source.

## Required GitHub Actions validation after applying

- Backend pytest suite.
- Frontend lint.
- Frontend production build.
- Existing phase gates.
- Visual check at desktop, tablet, and mobile widths.
