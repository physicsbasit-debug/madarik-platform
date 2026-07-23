#!/usr/bin/env python3
"""Deterministic repository and API audit for Phase 10-A.

The audit prefers Git's tracked-file inventory in CI. A filesystem fallback is
available for source ZIP validation before the package reaches GitHub.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


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
    "README.md",
    "CHANGELOG.md",
    "backend/app/core/release.py",
    "backend/app/models/release_readiness.py",
    "backend/app/services/release_readiness.py",
    "backend/tests/test_phase10_a_release_readiness.py",
    "backend/tests/test_phase10_a_end_to_end_acceptance.py",
    "docs/PHASE_10_A_RELEASE_HARDENING.md",
    "docs/FINAL_RELEASE_ACCEPTANCE_CHECKLIST.md",
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


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_audit(root: Path) -> int:
    errors: list[str] = []
    files = _git_files(root)
    inventory_mode = "git"
    if files is None:
        files = _filesystem_files(root)
        inventory_mode = "filesystem"
    file_set = set(files)

    missing = sorted(REQUIRED_FILES - file_set)
    if missing:
        _fail(errors, "Required release files are missing: " + ", ".join(missing))

    stray = sorted(name for name in ROOT_STRAY_NAMES if name in file_set)
    if stray:
        _fail(errors, "Stray files exist in repository root: " + ", ".join(stray))

    forbidden_generated: list[str] = []
    secret_files: list[str] = []
    for name in files:
        path = Path(name)
        if (
            "__pycache__" in path.parts
            or path.suffix.lower() in FORBIDDEN_GENERATED_SUFFIXES
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

        basename = path.name
        if basename == ".env" or (
            basename.startswith(".env.") and basename != ".env.example"
        ):
            secret_files.append(name)
        elif path.suffix.lower() in {".key", ".pem"}:
            secret_files.append(name)

    if forbidden_generated:
        _fail(
            errors,
            "Generated or release-artifact files are present: "
            + ", ".join(sorted(forbidden_generated)),
        )
    if secret_files:
        _fail(
            errors,
            "Secret-bearing file types are present: "
            + ", ".join(sorted(secret_files)),
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
        _fail(errors, "Possible secret material detected: " + ", ".join(findings))

    try:
        package = json.loads(_read_text(root / "frontend/package.json"))
        lock = json.loads(_read_text(root / "frontend/package-lock.json"))
        readme = _read_text(root / "README.md")
        release_source = _read_text(root / "backend/app/core/release.py")
    except (OSError, json.JSONDecodeError) as exc:
        _fail(errors, f"Version metadata could not be read: {exc}")
    else:
        package_version = str(package.get("version", ""))
        lock_version = str(lock.get("version", ""))
        readme_match = re.search(r"الإصدار البرمجي:\s*`([^`]+)`", readme)
        release_match = re.search(
            r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']',
            release_source,
            flags=re.MULTILINE,
        )
        versions = {
            "package": package_version,
            "package-lock": lock_version,
            "README": readme_match.group(1) if readme_match else "",
            "backend": release_match.group(1) if release_match else "",
        }
        if len(set(versions.values())) != 1 or not package_version:
            _fail(errors, f"Version metadata is inconsistent: {versions}")

    workflow_path = root / ".github/workflows/phase0-check.yml"
    if workflow_path.is_file():
        workflow = _read_text(workflow_path)
        for required_text in (
            "feat/madarik-science-platform-v2",
            "RUN_PHASE10_A_RELEASE_AUDIT.py",
            "npm run lint",
            "npm run build",
            "python -m pytest -q",
        ):
            if required_text not in workflow:
                _fail(errors, f"Workflow is missing required gate text: {required_text}")

    backend_path = str(root / "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    try:
        from fastapi.testclient import TestClient
        from app.main import app
    except Exception as exc:  # pragma: no cover - audit diagnostic
        _fail(errors, f"FastAPI application import failed: {exc}")
    else:
        operation_ids = [
            route.operation_id
            for route in app.routes
            if getattr(route, "operation_id", None)
        ]
        duplicates = sorted(
            key for key, count in Counter(operation_ids).items() if count > 1
        )
        if duplicates:
            _fail(errors, "Duplicate OpenAPI operation IDs: " + ", ".join(duplicates))

        openapi = app.openapi()
        paths = openapi.get("paths", {})
        if "/api/health/readiness" not in paths:
            _fail(errors, "Release readiness endpoint is absent from OpenAPI.")

        try:
            response = TestClient(app).get("/api/health/readiness")
        except Exception as exc:  # pragma: no cover - audit diagnostic
            _fail(errors, f"Readiness endpoint smoke failed: {exc}")
        else:
            if response.status_code != 200:
                _fail(errors, f"Readiness endpoint returned {response.status_code}.")
            else:
                payload = response.json()
                if payload.get("technical_ready") is not True:
                    _fail(errors, "Default technical readiness is blocked.")
                forbidden_fields = {
                    "api_key",
                    "client_secret",
                    "access_token",
                    "tenant_id",
                    "db_path",
                    "data_dir",
                }

                def collect_keys(value: object) -> set[str]:
                    if isinstance(value, dict):
                        keys = {str(key).casefold() for key in value}
                        for nested in value.values():
                            keys.update(collect_keys(nested))
                        return keys
                    if isinstance(value, list):
                        keys: set[str] = set()
                        for nested in value:
                            keys.update(collect_keys(nested))
                        return keys
                    return set()

                exposed = sorted(forbidden_fields & collect_keys(payload))
                if exposed:
                    _fail(
                        errors,
                        "Readiness payload exposes forbidden fields: "
                        + ", ".join(exposed),
                    )

    print("=== Phase 10-A Release Audit ===")
    print(f"Inventory mode: {inventory_mode}")
    print(f"Files inspected: {len(files)}")
    if errors:
        print(f"FAIL: {len(errors)} release audit issue(s)")
        for issue in errors:
            print(f"  - {issue}")
        return 1

    print("PASS: repository hygiene, version metadata, OpenAPI, and readiness.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository-root",
        default=Path(__file__).resolve().parent,
        type=Path,
    )
    args = parser.parse_args()
    return run_audit(args.repository_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
