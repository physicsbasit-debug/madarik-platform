#!/usr/bin/env python3
"""Deterministic final release-candidate preflight for Phase 10-B.

The preflight validates repository hygiene, release metadata, workflow
consolidation, final-release blockers, OpenAPI integrity, and the safe runtime
readiness endpoint. It uses Git's tracked-file inventory in CI and falls back
to a clean source-tree inventory for ZIP validation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

TARGET_VERSION = "2.0.0-rc.2"
TARGET_CHANNEL = "release-candidate"
TARGET_PHASE = "Phase 10-B"
TARGET_TITLE = "Final Release Candidate Consolidation and Sign-off"

EXCLUDED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "htmlcov",
    "node_modules",
}
FORBIDDEN_GENERATED_SUFFIXES = {
    ".db",
    ".patch",
    ".pyc",
    ".pyo",
    ".sqlite",
    ".sqlite3",
    ".zip",
}
BINARY_SUFFIXES = {
    ".docx",
    ".gif",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".ttf",
    ".webp",
    ".woff",
    ".woff2",
    ".xlsx",
}
ROOT_STRAY_NAMES = {
    "00_GITHUB_UPLOAD_PATHS.txt",
    "App.tsx",
    "CloudSources.tsx",
    "api.ts",
    "cloud_source_lifecycle.py",
    "cloud_source_repository.py",
    "cloud_source_version.py",
    "cloud_source_version_repository.py",
    "global.css",
    "project.ts",
    "projects.py",
    "test_phase9_c_cloud_version_history.py",
}
REQUIRED_FILES = {
    ".github/workflows/phase0-check.yml",
    "RUN_FINAL_RC_TESTS.sh",
    "RUN_PHASE10_A_RELEASE_AUDIT.py",
    "RUN_PHASE10_B_RC_PREFLIGHT.py",
    "README.md",
    "CHANGELOG.md",
    "backend/app/core/release.py",
    "backend/app/models/release_readiness.py",
    "backend/app/services/release_readiness.py",
    "backend/tests/test_phase10_a_release_readiness.py",
    "backend/tests/test_phase10_a_end_to_end_acceptance.py",
    "backend/tests/test_phase10_b_release_candidate.py",
    "docs/PHASE_10_A_RELEASE_HARDENING.md",
    "docs/PHASE_10_B_FINAL_RC_SIGNOFF.md",
    "docs/FINAL_RELEASE_ACCEPTANCE_CHECKLIST.md",
    "docs/FINAL_RELEASE_ACCEPTANCE.md",
    "docs/FINAL_RELEASE_STATUS.json",
    "frontend/package.json",
    "frontend/package-lock.json",
}
SECRET_PATTERNS = {
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
}
REQUIRED_OPEN_BLOCKERS = {
    "live_external_provider_acceptance",
    "visual_docx_pdf_review",
}


def _git_files(root: Path) -> list[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return [line for line in result.stdout.splitlines() if line]


def _filesystem_files(root: Path) -> list[str]:
    result: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRECTORIES for part in relative.parts):
            continue
        result.append(relative.as_posix())
    return sorted(result)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_assignment(source: str, name: str) -> str:
    match = re.search(
        rf'^{re.escape(name)}\s*=\s*["\']([^"\']+)["\']',
        source,
        flags=re.MULTILINE,
    )
    return match.group(1) if match else ""


def _release_workflow_files(root: Path, files: list[str]) -> list[str]:
    release_workflows: list[str] = []
    for name in files:
        if not name.startswith(".github/workflows/"):
            continue
        if Path(name).suffix.lower() not in {".yml", ".yaml"}:
            continue
        try:
            text = _read_text(root / name)
        except OSError:
            continue
        markers = (
            "RUN_PHASE10_B_RC_PREFLIGHT.py",
            "Backend full test suite",
            "Final RC",
            "Release Gate",
            "Final Release Checks",
        )
        if any(marker in text for marker in markers):
            release_workflows.append(name)
    return sorted(release_workflows)


def audit_repository(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    files = _git_files(root)
    inventory_mode = "git"
    if files is None:
        files = _filesystem_files(root)
        inventory_mode = "filesystem"
    file_set = set(files)

    missing = sorted(REQUIRED_FILES - file_set)
    if missing:
        errors.append("Required release files are missing: " + ", ".join(missing))

    stray = sorted(name for name in ROOT_STRAY_NAMES if name in file_set)
    if stray:
        errors.append("Stray files exist in repository root: " + ", ".join(stray))

    forbidden_generated: list[str] = []
    secret_files: list[str] = []
    for name in files:
        path = Path(name)
        suffix = path.suffix.lower()
        basename = path.name
        if (
            "__pycache__" in path.parts
            or suffix in FORBIDDEN_GENERATED_SUFFIXES
            or name.startswith(
                (
                    "backend/exports/",
                    "backend/generated/",
                    "backend/temp/",
                    "backend/uploads/",
                    "frontend/dist/",
                    "frontend/node_modules/",
                )
            )
        ):
            forbidden_generated.append(name)
        if basename == ".env" or (
            basename.startswith(".env.") and basename != ".env.example"
        ):
            secret_files.append(name)
        elif suffix in {".key", ".pem"}:
            secret_files.append(name)

    if forbidden_generated:
        errors.append(
            "Generated or release-artifact files are present: "
            + ", ".join(sorted(forbidden_generated))
        )
    if secret_files:
        errors.append(
            "Secret-bearing file types are present: "
            + ", ".join(sorted(secret_files))
        )

    findings: list[str] = []
    for name in files:
        path = root / name
        if not path.is_file() or path.suffix.lower() in BINARY_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = _read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{name}: {label}")
    if findings:
        errors.append("Possible secret material detected: " + ", ".join(findings))

    internal_registry_hits: list[str] = []
    registry_pattern = re.compile(
        r"packages\.applied-caas-gateway[A-Za-z0-9-]*\.internal\.api\.openai\.org"
    )
    for name in files:
        path = root / name
        if not path.is_file() or path.suffix.lower() in BINARY_SUFFIXES:
            continue
        try:
            text = _read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        if registry_pattern.search(text):
            internal_registry_hits.append(name)
    if internal_registry_hits:
        errors.append(
            "Internal CAAS registry URL is present: "
            + ", ".join(sorted(internal_registry_hits))
        )

    versions: dict[str, str] = {}
    release_values: dict[str, str] = {}
    try:
        package = json.loads(_read_text(root / "frontend/package.json"))
        lock = json.loads(_read_text(root / "frontend/package-lock.json"))
        readme = _read_text(root / "README.md")
        release_source = _read_text(root / "backend/app/core/release.py")
        status = json.loads(_read_text(root / "docs/FINAL_RELEASE_STATUS.json"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Release metadata could not be read: {exc}")
        status = {}
    else:
        readme_match = re.search(r"الإصدار البرمجي:\s*`([^`]+)`", readme)
        versions = {
            "package": str(package.get("version", "")),
            "package-lock": str(lock.get("version", "")),
            "package-lock-root": str(
                lock.get("packages", {}).get("", {}).get("version", "")
            ),
            "README": readme_match.group(1) if readme_match else "",
            "backend": _extract_assignment(release_source, "APP_VERSION"),
            "status": str(status.get("version", "")),
        }
        if set(versions.values()) != {TARGET_VERSION}:
            errors.append(f"Version metadata is inconsistent: {versions}")

        release_values = {
            "channel": _extract_assignment(release_source, "RELEASE_CHANNEL"),
            "phase": _extract_assignment(release_source, "RELEASE_PHASE"),
            "title": _extract_assignment(release_source, "RELEASE_TITLE"),
        }
        expected_release_values = {
            "channel": TARGET_CHANNEL,
            "phase": TARGET_PHASE,
            "title": TARGET_TITLE,
        }
        if release_values != expected_release_values:
            errors.append(
                "Backend release metadata is not Phase 10-B: "
                f"{release_values}"
            )

        if str(status.get("channel", "")) != TARGET_CHANNEL:
            errors.append("Final release status channel is inconsistent.")
        if str(status.get("phase", "")) != TARGET_PHASE:
            errors.append("Final release status phase is inconsistent.")
        if status.get("technical_candidate") != "ready_for_ci":
            errors.append("Technical candidate must be marked ready_for_ci.")
        if status.get("production_release") != "blocked":
            errors.append("Production release must remain blocked before live sign-off.")
        if status.get("tag_allowed") is not False:
            errors.append("Tag creation must remain disabled before final acceptance.")
        if status.get("github_release_allowed") is not False:
            errors.append(
                "GitHub Release creation must remain disabled before final acceptance."
            )
        blockers = status.get("blockers", [])
        open_blocker_ids = {
            str(item.get("id"))
            for item in blockers
            if isinstance(item, dict) and item.get("status") == "open"
        }
        if open_blocker_ids != REQUIRED_OPEN_BLOCKERS:
            errors.append(
                "Final release blockers are incomplete or inconsistent: "
                f"{sorted(open_blocker_ids)}"
            )

        required_readme_markers = (
            "Phase 10-B",
            "2.0.0-rc.2",
            "اختبار مزود خارجي حقيقي",
            "مراجعة DOCX/PDF بصريًا",
        )
        for marker in required_readme_markers:
            if marker not in readme:
                errors.append(f"README is missing current release marker: {marker}")

    release_workflows = _release_workflow_files(root, files)
    if len(release_workflows) != 1:
        errors.append(
            "Exactly one release-gate workflow is required; found: "
            + ", ".join(release_workflows)
        )
    elif release_workflows:
        workflow_path = root / release_workflows[0]
        workflow = _read_text(workflow_path)
        required_workflow_text = (
            "name: Phase 10-B Final RC Gate",
            "feat/madarik-science-platform-v2",
            "RUN_PHASE10_B_RC_PREFLIGHT.py",
            "test_phase10_b_release_candidate.py",
            "python -m pytest -q",
            "npm ci",
            "npm run lint",
            "npm run build",
            "actions/upload-artifact@v4",
        )
        for marker in required_workflow_text:
            if marker not in workflow:
                errors.append(f"Release workflow is missing required gate text: {marker}")
        stale_markers = (
            "name: Final Release Checks",
            "name: Phase 10-A Release Gate",
        )
        for marker in stale_markers:
            if marker in workflow:
                errors.append(f"Release workflow still uses stale identity: {marker}")

    acceptance = root / "docs/FINAL_RELEASE_ACCEPTANCE.md"
    checklist = root / "docs/FINAL_RELEASE_ACCEPTANCE_CHECKLIST.md"
    for path in (acceptance, checklist):
        if path.is_file():
            text = _read_text(path)
            if TARGET_VERSION not in text:
                errors.append(f"{path.name} does not reference {TARGET_VERSION}.")
            if TARGET_PHASE not in text:
                errors.append(f"{path.name} does not reference {TARGET_PHASE}.")

    backend_path = str(root / "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    openapi_paths = 0
    openapi_operations = 0
    duplicate_operation_ids: list[str] = []
    readiness_state = "unavailable"

    runtime_directory = tempfile.TemporaryDirectory(
        prefix="madarik-phase10b-preflight-"
    )
    previous_environment = {
        "MADARIK_DATA_DIR": os.environ.get("MADARIK_DATA_DIR"),
        "MADARIK_DB_PATH": os.environ.get("MADARIK_DB_PATH"),
    }
    os.environ["MADARIK_DATA_DIR"] = runtime_directory.name
    os.environ["MADARIK_DB_PATH"] = str(
        Path(runtime_directory.name) / "madarik.sqlite3"
    )

    try:
        from fastapi.testclient import TestClient
        from app.main import app
    except Exception as exc:  # pragma: no cover - diagnostic path
        errors.append(f"FastAPI application import failed: {exc}")
    else:
        operation_ids = [
            route.operation_id
            for route in app.routes
            if getattr(route, "operation_id", None)
        ]
        duplicate_operation_ids = sorted(
            key for key, count in Counter(operation_ids).items() if count > 1
        )
        if duplicate_operation_ids:
            errors.append(
                "Duplicate OpenAPI operation IDs: "
                + ", ".join(duplicate_operation_ids)
            )

        openapi = app.openapi()
        paths = openapi.get("paths", {})
        openapi_paths = len(paths)
        openapi_operations = sum(
            1
            for methods in paths.values()
            if isinstance(methods, dict)
            for method in methods
            if method.lower()
            in {"get", "post", "put", "patch", "delete", "options", "head"}
        )
        if "/api/health/readiness" not in paths:
            errors.append("Release readiness endpoint is absent from OpenAPI.")

        try:
            response = TestClient(app).get("/api/health/readiness")
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors.append(f"Readiness endpoint smoke failed: {exc}")
        else:
            if response.status_code != 200:
                errors.append(
                    f"Readiness endpoint returned {response.status_code}."
                )
            else:
                payload = response.json()
                readiness_state = str(payload.get("state", ""))
                expected_payload = {
                    "version": TARGET_VERSION,
                    "channel": TARGET_CHANNEL,
                    "phase": TARGET_PHASE,
                    "phase_title": TARGET_TITLE,
                }
                actual_payload = {
                    key: payload.get(key) for key in expected_payload
                }
                if actual_payload != expected_payload:
                    errors.append(
                        "Readiness release metadata is inconsistent: "
                        f"{actual_payload}"
                    )
                if payload.get("technical_ready") is not True:
                    errors.append("Default technical readiness is blocked.")
                forbidden_keys = {
                    "api_key",
                    "client_secret",
                    "tenant_id",
                    "db_path",
                    "data_dir",
                }

                def collect_keys(value: object) -> set[str]:
                    if isinstance(value, dict):
                        result = {str(key).lower() for key in value}
                        for child in value.values():
                            result.update(collect_keys(child))
                        return result
                    if isinstance(value, list):
                        result: set[str] = set()
                        for child in value:
                            result.update(collect_keys(child))
                        return result
                    return set()

                leaked = sorted(forbidden_keys & collect_keys(payload))
                if leaked:
                    errors.append(
                        "Readiness payload exposes forbidden fields: "
                        + ", ".join(leaked)
                    )
    finally:
        runtime_directory.cleanup()
        for key, value in previous_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    return {
        "ok": not errors,
        "phase": TARGET_PHASE,
        "version": TARGET_VERSION,
        "inventory_mode": inventory_mode,
        "files_inspected": len(files),
        "errors": errors,
        "warnings": warnings,
        "versions": versions,
        "release_metadata": release_values,
        "release_workflows": release_workflows,
        "openapi_paths": openapi_paths,
        "openapi_operations": openapi_operations,
        "duplicate_operation_ids": duplicate_operation_ids,
        "readiness_state": readiness_state,
        "production_release": "blocked",
        "open_blockers": sorted(REQUIRED_OPEN_BLOCKERS),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    root = args.repository_root.resolve()
    report = audit_repository(root)

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("=== Phase 10-B Final RC Preflight ===")
    print(f"Inventory mode: {report['inventory_mode']}")
    print(f"Files inspected: {report['files_inspected']}")
    print(f"Version: {report['version']}")
    print(f"Release workflows: {len(report['release_workflows'])}")
    print(
        "OpenAPI: "
        f"{report['openapi_paths']} paths / "
        f"{report['openapi_operations']} operations"
    )

    if report["errors"]:
        for message in report["errors"]:
            print(f"FAIL: {message}")
        return 1

    for message in report["warnings"]:
        print(f"WARN: {message}")
    print("PASS: final RC metadata, workflow, blockers, repository, OpenAPI, and readiness.")
    print("LIVE BLOCKERS remain open by design; production release and tagging are disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
