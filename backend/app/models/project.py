from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class OutputMode(str, Enum):
    arabic = "arabic"
    bilingual = "bilingual"


class ProjectMetadata(BaseModel):
    school_name: str = ""
    directorate: str = ""
    subject: str = ""
    grade: str = ""
    semester: str = ""
    paper_title: str = ""
    duration: str = ""
    total_marks: str = ""
    teacher_name: str = ""
    date: str = ""
    output_mode: OutputMode = OutputMode.arabic


class ProjectSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    current_step: str = "setup"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
