from __future__ import annotations

import sqlite3
from pathlib import Path

from app.core.config import settings
from app.models.project import ProjectSession


class ProjectRepository:
    """SQLite-backed repository for Phase 2-A1.

    The app still keeps an in-memory cache for speed and simple object mutation,
    but every committed project state is mirrored to SQLite. This gives Phase 2
    a durable foundation without introducing accounts, users, or a full database
    circus before the tent is even standing.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    owner_account_id TEXT,
                    title TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            self._ensure_owner_column(connection)
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_projects_owner_account_id ON projects(owner_account_id)"
            )

    def _ensure_owner_column(self, connection: sqlite3.Connection) -> None:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(projects)").fetchall()
        }
        if "owner_account_id" not in columns:
            connection.execute("ALTER TABLE projects ADD COLUMN owner_account_id TEXT")

    def save(self, project: ProjectSession) -> ProjectSession:
        payload = project.model_dump_json()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO projects (id, owner_account_id, title, subject, grade, updated_at, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    owner_account_id = excluded.owner_account_id,
                    title = excluded.title,
                    subject = excluded.subject,
                    grade = excluded.grade,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    project.id,
                    project.owner_account_id,
                    project.metadata.paper_title,
                    project.metadata.subject,
                    project.metadata.grade,
                    project.updated_at.isoformat(),
                    payload,
                ),
            )
        return project

    def load(self, project_id: str) -> ProjectSession | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()

        if row is None:
            return None

        return ProjectSession.model_validate_json(row["payload"])

    def delete(self, project_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0

    def list_recent(
        self,
        limit: int = 50,
        account_id: str | None = None,
        include_all: bool = True,
    ) -> list[ProjectSession]:
        safe_limit = max(1, min(limit, 200))
        with self._connect() as connection:
            if include_all:
                rows = connection.execute(
                    "SELECT payload FROM projects ORDER BY updated_at DESC LIMIT ?",
                    (safe_limit,),
                ).fetchall()
            elif account_id is None:
                rows = connection.execute(
                    """
                    SELECT payload
                    FROM projects
                    WHERE owner_account_id IS NULL
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (safe_limit,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT payload
                    FROM projects
                    WHERE owner_account_id = ? OR owner_account_id IS NULL
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (account_id, safe_limit),
                ).fetchall()

        return [ProjectSession.model_validate_json(row["payload"]) for row in rows]


project_repository = ProjectRepository()
