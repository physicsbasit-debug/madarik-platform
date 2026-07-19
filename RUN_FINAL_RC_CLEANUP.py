#!/usr/bin/env python3
"""Remove generated Python bytecode that was accidentally committed.

This script intentionally removes only deterministic generated Python artifacts.
It does not delete databases, uploads, exports, snapshots, environments, or user data.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
}


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout


tracked = git_output("ls-files").splitlines()
generated_tracked = [
    path
    for path in tracked
    if "__pycache__" in Path(path).parts
    or Path(path).suffix.lower() in {".pyc", ".pyo"}
]

if generated_tracked:
    subprocess.run(
        ["git", "rm", "-f", "--", *generated_tracked],
        cwd=ROOT,
        check=True,
    )
    print(f"Removed {len(generated_tracked)} tracked Python generated file(s).")
else:
    print("No tracked Python generated files were found.")

removed_dirs = 0
for current_root, dirnames, _filenames in os.walk(ROOT):
    dirnames[:] = [
        name for name in dirnames
        if name not in SKIP_DIRS
    ]

    current = Path(current_root)
    if current.name == "__pycache__":
        shutil.rmtree(current)
        removed_dirs += 1
        dirnames[:] = []

print(f"Removed {removed_dirs} local project __pycache__ directorie(s).")
print("Cleanup complete. Review git status before committing.")
