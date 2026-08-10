"""Dogfood: bandit stays clean on modules that --check commonly scans."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_BANDIT_TARGETS = (
    "src/diffrat/checks.py",
    "src/diffrat/review_quality.py",
    "src/diffrat/scoring.py",
)


@pytest.mark.skipif(shutil.which("bandit") is None, reason="bandit not installed")
def test_bandit_clean_on_check_dogfood_modules() -> None:
    completed = subprocess.run(
        ["bandit", "-r", *_BANDIT_TARGETS],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
