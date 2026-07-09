# API Spec - منصة مدارك

## Health

GET /api/health

## Projects

POST /api/projects

DELETE /api/projects/{project_id}

## Upload

POST /api/projects/{project_id}/upload

## Extract

POST /api/projects/{project_id}/extract

## Glossary

POST /api/projects/{project_id}/glossary

PATCH /api/projects/{project_id}/glossary/{term_id}

## Translation

POST /api/projects/{project_id}/translate

## Questions

PATCH /api/projects/{project_id}/questions/{question_id}

POST /api/projects/{project_id}/questions/reorder

## Export

POST /api/projects/{project_id}/export
