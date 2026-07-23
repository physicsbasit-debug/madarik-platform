from fastapi import APIRouter

from app.core.release import APP_VERSION, RELEASE_PHASE
from app.models.release_readiness import ReleaseReadinessReport
from app.services.release_readiness import build_release_readiness_report

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a small health payload for smoke testing."""

    return {
        "status": "ok",
        "service": "madarik-api",
        "version": APP_VERSION,
        "phase": RELEASE_PHASE,
    }


@router.get(
    "/health/readiness",
    response_model=ReleaseReadinessReport,
)
def release_readiness() -> ReleaseReadinessReport:
    """Return safe technical release readiness without exposing secrets."""

    return build_release_readiness_report()
