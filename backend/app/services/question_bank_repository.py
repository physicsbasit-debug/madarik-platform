from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.models.project import ProjectSession, QuestionItem
from app.models.question_bank import QuestionBankItem


def build_question_fingerprint(
    question: QuestionItem,
) -> str:
    parts = [
        question.original_text.strip(),
        question.translated_text.strip(),
        str(question.marks),
        question.cognitive_category.value,
        str(question.curriculum_grade),
        question.curriculum_subject_id or "",
        question.curriculum_unit_id or "",
        question.curriculum_lesson_id or "",
        ",".join(
            sorted(
                question.curriculum_learning_outcome_ids
            )
        ),
    ]
    payload = "\n".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class QuestionBankRepository:
    def __init__(
        self,
        db_path: str | Path | None = None,
    ) -> None:
        self.db_path = Path(
            db_path or settings.db_path
        )
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS question_bank (
                    id TEXT PRIMARY KEY,
                    source_project_id TEXT NOT NULL,
                    source_question_id TEXT NOT NULL,
                    owner_account_id TEXT,
                    content_fingerprint TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    UNIQUE(
                        source_project_id,
                        source_question_id
                    )
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_question_bank_project
                ON question_bank(source_project_id)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_question_bank_owner
                ON question_bank(owner_account_id)
                """
            )

    def save_from_project_question(
        self,
        project: ProjectSession,
        question: QuestionItem,
    ) -> QuestionBankItem:
        fingerprint = build_question_fingerprint(
            question
        )
        existing = self.get_by_source(
            project.id,
            question.id,
        )
        now = datetime.now(timezone.utc)

        if existing is None:
            item = QuestionBankItem(
                source_project_id=project.id,
                source_question_id=question.id,
                owner_account_id=project.owner_account_id,
                content_fingerprint=fingerprint,
                question_snapshot=question.model_copy(
                    deep=True
                ),
                created_at=now,
                updated_at=now,
            )
        else:
            item = existing.model_copy(
                update={
                    "owner_account_id":
                        project.owner_account_id,
                    "content_fingerprint": fingerprint,
                    "question_snapshot":
                        question.model_copy(deep=True),
                    "updated_at": now,
                },
                deep=True,
            )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO question_bank (
                    id,
                    source_project_id,
                    source_question_id,
                    owner_account_id,
                    content_fingerprint,
                    updated_at,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    source_project_id,
                    source_question_id
                )
                DO UPDATE SET
                    owner_account_id =
                        excluded.owner_account_id,
                    content_fingerprint =
                        excluded.content_fingerprint,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    item.id,
                    item.source_project_id,
                    item.source_question_id,
                    item.owner_account_id,
                    item.content_fingerprint,
                    item.updated_at.isoformat(),
                    item.model_dump_json(),
                ),
            )

        return item

    def get_by_source(
        self,
        project_id: str,
        question_id: str,
    ) -> QuestionBankItem | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM question_bank
                WHERE source_project_id = ?
                  AND source_question_id = ?
                """,
                (project_id, question_id),
            ).fetchone()

        if row is None:
            return None
        return QuestionBankItem.model_validate_json(
            row["payload"]
        )

    def list_for_project(
        self,
        project_id: str,
    ) -> list[QuestionBankItem]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM question_bank
                WHERE source_project_id = ?
                ORDER BY updated_at DESC
                """,
                (project_id,),
            ).fetchall()

        return [
            QuestionBankItem.model_validate_json(
                row["payload"]
            )
            for row in rows
        ]

    def delete(
        self,
        project_id: str,
        item_id: str,
    ) -> QuestionBankItem | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM question_bank
                WHERE id = ?
                  AND source_project_id = ?
                """,
                (item_id, project_id),
            ).fetchone()

            if row is None:
                return None

            connection.execute(
                """
                DELETE FROM question_bank
                WHERE id = ?
                  AND source_project_id = ?
                """,
                (item_id, project_id),
            )

        return QuestionBankItem.model_validate_json(
            row["payload"]
        )


question_bank_repository = QuestionBankRepository()
