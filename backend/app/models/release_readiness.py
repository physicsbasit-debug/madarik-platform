from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class ReleaseCheckStatus(str, Enum):
    passed = "passed"
    warning = "warning"
    failed = "failed"


class ReleaseReadinessState(str, Enum):
    ready = "ready"
    degraded = "degraded"
    blocked = "blocked"


class ReleaseReadinessCheck(BaseModel):
    key: str
    label: str
    status: ReleaseCheckStatus
    required: bool = True
    message: str


class ReleaseProviderReadiness(BaseModel):
    provider: str
    mode: str
    enabled: bool
    configured: bool
    ready: bool
    required_for_technical_gate: bool = False
    message: str


class ReleaseReadinessReport(BaseModel):
    service: str = "madarik-api"
    version: str
    channel: str
    phase: str
    phase_title: str
    state: ReleaseReadinessState
    technical_ready: bool
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    blocking_count: int = Field(default=0, ge=0)
    warning_count: int = Field(default=0, ge=0)
    checks: list[ReleaseReadinessCheck] = Field(default_factory=list)
    providers: list[ReleaseProviderReadiness] = Field(default_factory=list)
    live_external_acceptance_required: bool = True
    live_external_acceptance_completed: bool = False
