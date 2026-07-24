# Madarik Simplified User Journey — Batch 7 Fix 2

Target branch: `feat/madarik-science-platform-v2`

## Scope

- Restore the `questions: QuestionItem[]` prop expected by the existing `App.tsx` call to `StartWorkspace`.
- Preserve all Batch 7 work-library behavior and callbacks.
- Add a focused release-gate regression test for the complete question/layout/parse contract.
- No Backend, API, persistence, translation, review, or export behavior changes.

## Why this fix exists

Batch 7 Fix 1 restored `layoutAssets`, `onDeleteLayoutAsset`, and `onParseQuestions`, but the current `App.tsx` also passes the project `questions` array. TypeScript correctly rejected the incomplete component prop contract.

## Upload

Upload the extracted `frontend`, `backend`, and this README to the repository root on the same branch. Do not upload the ZIP itself.
