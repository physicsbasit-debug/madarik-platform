from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from app.core.config import Settings, settings
from app.core.release import (
    APP_VERSION,
    RELEASE_CHANNEL,
    RELEASE_PHASE,
    RELEASE_TITLE,
)
from app.models.release_readiness import (
    ReleaseCheckStatus,
    ReleaseProviderReadiness,
    ReleaseReadinessCheck,
    ReleaseReadinessReport,
    ReleaseReadinessState,
)


EXPECTED_DATABASE_TABLES = frozenset(
    {
        "assessments",
        "auth_accounts",
        "auth_sessions",
        "cloud_source_versions",
        "cloud_sources",
        "differentiated_activities",
        "projects",
        "question_bank",
        "scientific_diagrams",
    }
)
SUPPORTED_AI_PROVIDERS = frozenset(
    {"mock", "gemini", "openai", "openai-compatible"}
)


def _passed(key: str, label: str, message: str) -> ReleaseReadinessCheck:
    return ReleaseReadinessCheck(
        key=key,
        label=label,
        status=ReleaseCheckStatus.passed,
        message=message,
    )


def _warning(
    key: str,
    label: str,
    message: str,
    *,
    required: bool = False,
) -> ReleaseReadinessCheck:
    return ReleaseReadinessCheck(
        key=key,
        label=label,
        status=ReleaseCheckStatus.warning,
        required=required,
        message=message,
    )


def _failed(key: str, label: str, message: str) -> ReleaseReadinessCheck:
    return ReleaseReadinessCheck(
        key=key,
        label=label,
        status=ReleaseCheckStatus.failed,
        message=message,
    )


def _database_checks(db_path: Path) -> list[ReleaseReadinessCheck]:
    label = "قاعدة البيانات"
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as connection:
            quick_check = connection.execute("PRAGMA quick_check").fetchone()
            tables = {
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
    except (OSError, sqlite3.Error):
        return [
            _failed(
                "database_connection",
                label,
                "تعذر فتح قاعدة البيانات أو فحص سلامتها.",
            )
        ]

    checks = [
        _passed(
            "database_connection",
            label,
            "قاعدة البيانات قابلة للفتح والاستعلام.",
        )
        if quick_check and quick_check[0] == "ok"
        else _failed(
            "database_connection",
            label,
            "فحص SQLite الداخلي لم يرجع حالة سليمة.",
        )
    ]

    missing = sorted(EXPECTED_DATABASE_TABLES - tables)
    if missing:
        checks.append(
            _failed(
                "database_schema",
                "مخطط قاعدة البيانات",
                "الجداول المطلوبة غير مكتملة: " + ", ".join(missing),
            )
        )
    else:
        checks.append(
            _passed(
                "database_schema",
                "مخطط قاعدة البيانات",
                "جميع جداول التطبيق الأساسية مهيأة.",
            )
        )
    return checks


def _writable_directory_check(
    path: Path,
    *,
    key: str,
    label: str,
) -> ReleaseReadinessCheck:
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix="madarik-readiness-",
            dir=path,
            delete=True,
        ) as handle:
            handle.write(b"ok")
            handle.flush()
    except OSError:
        return _failed(
            key,
            label,
            "المجلد غير قابل للإنشاء أو الكتابة.",
        )
    return _passed(
        key,
        label,
        "المجلد قابل للإنشاء والكتابة.",
    )


def _ai_provider(runtime: Settings) -> tuple[
    ReleaseProviderReadiness,
    ReleaseReadinessCheck,
]:
    provider = runtime.ai_provider.strip().lower() or "mock"
    enabled = runtime.ai_external_enabled
    supported = provider in SUPPORTED_AI_PROVIDERS

    if not enabled:
        return (
            ReleaseProviderReadiness(
                provider="translation",
                mode=provider,
                enabled=False,
                configured=provider == "mock",
                ready=provider == "mock",
                message=(
                    "الوضع المحلي الآمن مفعل، والقبول الحي للمزود الخارجي "
                    "ما زال مطلوبًا قبل الإصدار النهائي."
                ),
            ),
            _warning(
                "translation_provider",
                "مزود الترجمة",
                "الاتصال الخارجي غير مفعل؛ الاختبارات المحلية تستخدم الوضع الآمن.",
            ),
        )

    if not supported or provider == "mock":
        return (
            ReleaseProviderReadiness(
                provider="translation",
                mode=provider,
                enabled=True,
                configured=False,
                ready=False,
                required_for_technical_gate=True,
                message="تم تفعيل الاتصال الخارجي دون اختيار مزود خارجي مدعوم.",
            ),
            _failed(
                "translation_provider",
                "مزود الترجمة",
                "إعداد مزود الترجمة الخارجي غير صالح.",
            ),
        )

    if provider == "gemini":
        configured = bool(
            runtime.gemini_api_key.strip()
            and runtime.gemini_model.strip()
            and runtime.gemini_base_url.strip()
        )
    else:
        configured = bool(
            runtime.ai_api_key.strip()
            and runtime.ai_model.strip()
            and runtime.ai_base_url.strip()
        )

    if configured:
        return (
            ReleaseProviderReadiness(
                provider="translation",
                mode=provider,
                enabled=True,
                configured=True,
                ready=True,
                required_for_technical_gate=True,
                message="إعداد المزود الخارجي مكتمل دون عرض أي بيانات سرية.",
            ),
            _passed(
                "translation_provider",
                "مزود الترجمة",
                "إعداد المزود الخارجي مكتمل.",
            ),
        )

    return (
        ReleaseProviderReadiness(
            provider="translation",
            mode=provider,
            enabled=True,
            configured=False,
            ready=False,
            required_for_technical_gate=True,
            message="إعداد المزود الخارجي ناقص.",
        ),
        _failed(
            "translation_provider",
            "مزود الترجمة",
            "الاتصال الخارجي مفعل لكن المفتاح أو النموذج أو العنوان غير مكتمل.",
        ),
    )


def _google_drive_provider(runtime: Settings) -> tuple[
    ReleaseProviderReadiness,
    ReleaseReadinessCheck,
]:
    mode = runtime.google_drive_provider.strip().lower() or "disabled"
    if mode == "disabled":
        return (
            ReleaseProviderReadiness(
                provider="google-drive",
                mode=mode,
                enabled=False,
                configured=False,
                ready=False,
                message="تكامل Google Drive معطل اختياريًا.",
            ),
            _warning(
                "google_drive_provider",
                "Google Drive",
                "التكامل معطل ولا يمنع البوابة التقنية.",
            ),
        )

    if mode == "mock":
        return (
            ReleaseProviderReadiness(
                provider="google-drive",
                mode=mode,
                enabled=True,
                configured=True,
                ready=True,
                message="مزود Google Drive التجريبي جاهز للاختبارات المحلية.",
            ),
            _passed(
                "google_drive_provider",
                "Google Drive",
                "المزود التجريبي جاهز.",
            ),
        )

    configured = bool(
        mode == "google_api"
        and runtime.google_drive_access_token.strip()
        and runtime.google_drive_folder_id.strip()
    )
    if configured:
        return (
            ReleaseProviderReadiness(
                provider="google-drive",
                mode=mode,
                enabled=True,
                configured=True,
                ready=True,
                message="إعداد Google Drive مكتمل دون كشف الرمز أو معرف المجلد.",
            ),
            _passed(
                "google_drive_provider",
                "Google Drive",
                "إعداد التكامل مكتمل.",
            ),
        )

    return (
        ReleaseProviderReadiness(
            provider="google-drive",
            mode=mode,
            enabled=True,
            configured=False,
            ready=False,
            required_for_technical_gate=True,
            message="إعداد Google Drive المفعل غير مكتمل.",
        ),
        _failed(
            "google_drive_provider",
            "Google Drive",
            "التكامل مفعل لكن الرمز أو معرف المجلد غير مكتمل.",
        ),
    )


def _onedrive_provider(runtime: Settings) -> tuple[
    ReleaseProviderReadiness,
    ReleaseReadinessCheck,
]:
    mode = runtime.onedrive_provider.strip().lower() or "disabled"
    if mode == "disabled":
        return (
            ReleaseProviderReadiness(
                provider="onedrive",
                mode=mode,
                enabled=False,
                configured=False,
                ready=False,
                message="تكامل OneDrive معطل اختياريًا.",
            ),
            _warning(
                "onedrive_provider",
                "OneDrive",
                "التكامل معطل ولا يمنع البوابة التقنية.",
            ),
        )

    configured = bool(
        mode == "graph"
        and runtime.onedrive_tenant_id.strip()
        and runtime.onedrive_client_id.strip()
        and runtime.onedrive_client_secret.strip()
        and runtime.onedrive_graph_base_url.strip()
    )
    if configured:
        return (
            ReleaseProviderReadiness(
                provider="onedrive",
                mode=mode,
                enabled=True,
                configured=True,
                ready=True,
                message="إعداد Microsoft Graph مكتمل دون كشف بيانات الاعتماد.",
            ),
            _passed(
                "onedrive_provider",
                "OneDrive",
                "إعداد Microsoft Graph مكتمل.",
            ),
        )

    return (
        ReleaseProviderReadiness(
            provider="onedrive",
            mode=mode,
            enabled=True,
            configured=False,
            ready=False,
            required_for_technical_gate=True,
            message="إعداد OneDrive المفعل غير مكتمل.",
        ),
        _failed(
            "onedrive_provider",
            "OneDrive",
            "التكامل مفعل لكن بيانات Microsoft Graph غير مكتملة.",
        ),
    )


def build_release_readiness_report(
    runtime_settings: Settings | None = None,
    *,
    db_path: str | Path | None = None,
    data_dir: str | Path | None = None,
) -> ReleaseReadinessReport:
    """Build a safe runtime release-readiness report.

    The payload intentionally exposes booleans, modes, and human-readable
    summaries only. It never returns tokens, secrets, database paths, or file
    system paths.
    """

    runtime = runtime_settings or settings
    resolved_db_path = Path(db_path or runtime.db_path)
    resolved_data_dir = Path(data_dir or runtime.data_dir)

    checks = _database_checks(resolved_db_path)
    checks.extend(
        [
            _writable_directory_check(
                resolved_data_dir,
                key="data_directory",
                label="مجلد البيانات",
            ),
            _writable_directory_check(
                resolved_data_dir / "exports",
                key="export_directory",
                label="مجلد التصدير",
            ),
        ]
    )

    providers: list[ReleaseProviderReadiness] = []
    for builder in (
        _ai_provider,
        _google_drive_provider,
        _onedrive_provider,
    ):
        provider, check = builder(runtime)
        providers.append(provider)
        checks.append(check)

    blocking_count = sum(
        1
        for check in checks
        if check.required and check.status is ReleaseCheckStatus.failed
    )
    warning_count = sum(
        1
        for check in checks
        if check.status is ReleaseCheckStatus.warning
    )
    technical_ready = blocking_count == 0
    if not technical_ready:
        state = ReleaseReadinessState.blocked
    elif warning_count:
        state = ReleaseReadinessState.degraded
    else:
        state = ReleaseReadinessState.ready

    return ReleaseReadinessReport(
        version=APP_VERSION,
        channel=RELEASE_CHANNEL,
        phase=RELEASE_PHASE,
        phase_title=RELEASE_TITLE,
        state=state,
        technical_ready=technical_ready,
        blocking_count=blocking_count,
        warning_count=warning_count,
        checks=checks,
        providers=providers,
    )
