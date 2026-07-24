# Madarik Simplified User Journey — Batch 7

## Scope

This batch simplifies the **أعمالي** entry step without changing Backend contracts or project persistence.

### Visible changes

- One clear library titled **أعمالي**.
- Search by work title or uploaded filename.
- Simple filters: all, current, needs review, ready, drafts.
- Current work card with one appropriate action:
  - continue when content exists;
  - upload a file when the current work is still empty.
- Saved work cards expose real actions only: open/continue and delete.
- Bulk selection and deletion are hidden under **إدارة متقدمة**.
- Responsive layouts for desktop, tablet, and mobile.

### Intentionally unchanged

- SQLite project persistence.
- Project API contracts.
- Upload and extraction logic.
- Review and export engines.
- Assessment, activity, and question-bank modules.

## GitHub target

Apply directly to:

`feat/madarik-science-platform-v2`

Do not create another branch.
