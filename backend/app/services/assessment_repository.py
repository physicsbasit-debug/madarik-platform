from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.models.assessment import (
    AssessmentBlueprint,
    AssessmentDraft,
    AssessmentLayoutUpdate,
    AssessmentItemConfiguration,
)
from app.models.question_bank import QuestionBankItem


class AssessmentRepository:
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
                CREATE TABLE IF NOT EXISTS assessments (
                    id TEXT PRIMARY KEY,
                    owner_account_id TEXT,
                    source_project_id TEXT,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_assessments_owner
                ON assessments(owner_account_id)
                """
            )

    def save(self, draft: AssessmentDraft) -> AssessmentDraft:
        draft.updated_at = datetime.now(timezone.utc)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO assessments (
                    id,
                    owner_account_id,
                    source_project_id,
                    updated_at,
                    payload
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id)
                DO UPDATE SET
                    owner_account_id = excluded.owner_account_id,
                    source_project_id = excluded.source_project_id,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    draft.id,
                    draft.owner_account_id,
                    draft.source_project_id,
                    draft.updated_at.isoformat(),
                    draft.model_dump_json(),
                ),
            )
        return draft

    def create(
        self,
        *,
        blueprint: AssessmentBlueprint,
        owner_account_id: str | None,
        source_project_id: str | None,
    ) -> AssessmentDraft:
        draft = AssessmentDraft(
            owner_account_id=owner_account_id,
            source_project_id=source_project_id,
            blueprint=blueprint,
        )
        return self.save(draft)

    def get(self, draft_id: str) -> AssessmentDraft | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM assessments WHERE id = ?",
                (draft_id,),
            ).fetchone()
        if row is None:
            return None
        return AssessmentDraft.model_validate_json(row["payload"])

    def list(
        self,
        *,
        owner_account_id: str | None = None,
    ) -> list[AssessmentDraft]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM assessments
                ORDER BY updated_at DESC
                """
            ).fetchall()
        items = [
            AssessmentDraft.model_validate_json(row["payload"])
            for row in rows
        ]
        if owner_account_id:
            items = [
                item
                for item in items
                if item.owner_account_id == owner_account_id
            ]
        return items

    def update_blueprint(
        self,
        draft: AssessmentDraft,
        blueprint: AssessmentBlueprint,
    ) -> AssessmentDraft:
        draft.blueprint = blueprint
        return self.save(draft)

    def add_bank_item(
        self,
        draft: AssessmentDraft,
        bank_item: QuestionBankItem,
    ) -> tuple[AssessmentDraft, bool]:
        if bank_item.id in draft.question_bank_item_ids:
            return draft, False
        draft.question_bank_item_ids.append(bank_item.id)
        self.normalize_item_configurations(draft)
        self.save(draft)
        return draft, True

    def remove_bank_item(
        self,
        draft: AssessmentDraft,
        bank_item_id: str,
    ) -> tuple[AssessmentDraft, bool]:
        if bank_item_id not in draft.question_bank_item_ids:
            return draft, False
        draft.question_bank_item_ids = [
            item_id
            for item_id in draft.question_bank_item_ids
            if item_id != bank_item_id
        ]
        self.normalize_item_configurations(draft)
        self.save(draft)
        return draft, True



    def update_layout(
        self,
        draft: AssessmentDraft,
        layout: AssessmentLayoutUpdate,
    ) -> AssessmentDraft:
        valid_ids = set(draft.question_bank_item_ids)
        section_ids = {
            section.id for section in layout.sections
        }

        draft.sections = sorted(
            layout.sections,
            key=lambda section: section.order_index,
        ) or draft.sections

        normalized: list[
            AssessmentItemConfiguration
        ] = []
        seen: set[str] = set()

        for config in sorted(
            layout.item_configurations,
            key=lambda item: item.order_index,
        ):
            if (
                config.bank_item_id not in valid_ids
                or config.bank_item_id in seen
            ):
                continue
            seen.add(config.bank_item_id)
            normalized.append(
                config.model_copy(
                    update={
                        "section_id": (
                            config.section_id
                            if config.section_id
                            in section_ids
                            else None
                        )
                    }
                )
            )

        next_order = len(normalized) + 1
        for bank_item_id in draft.question_bank_item_ids:
            if bank_item_id in seen:
                continue
            normalized.append(
                AssessmentItemConfiguration(
                    bank_item_id=bank_item_id,
                    order_index=next_order,
                )
            )
            next_order += 1

        draft.item_configurations = normalized
        return self.save(draft)

    def normalize_item_configurations(
        self,
        draft: AssessmentDraft,
    ) -> AssessmentDraft:
        valid_ids = set(draft.question_bank_item_ids)
        existing = {
            config.bank_item_id: config
            for config in draft.item_configurations
            if config.bank_item_id in valid_ids
        }

        normalized = []
        for index, bank_item_id in enumerate(
            draft.question_bank_item_ids,
            start=1,
        ):
            config = existing.get(bank_item_id)
            normalized.append(
                (
                    config.model_copy(
                        update={"order_index": index}
                    )
                    if config
                    else AssessmentItemConfiguration(
                        bank_item_id=bank_item_id,
                        order_index=index,
                    )
                )
            )

        draft.item_configurations = normalized
        return draft

assessment_repository = AssessmentRepository()
