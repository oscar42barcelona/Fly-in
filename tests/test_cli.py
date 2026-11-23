"""Smoke tests for the real Fly-in CLI and scheduling integration."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Execute the public CLI as an external process."""
    return subprocess.run(
        [sys.executable, "cli.py", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )


def test_linear_map_completes_in_four_turns() -> None:
    """Two drones on the linear map must arrive in four turns."""
    result = run_cli("maps/easy/01_linear_path.txt")
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 4
    assert lines[-1] == "D2-goal"
    assert sum(line.count("-goal") for line in lines) == 2
    assert all(
        re.fullmatch(r"D[0-9]+-\S+(?: D[0-9]+-\S+)*", line)
        for line in lines
    )


def test_missing_map_is_a_cli_error() -> None:
    """Missing input should report an error without an uncaught traceback."""
    result = run_cli("maps/does-not-exist.txt")
    assert result.returncode != 0
    assert "Error:" in result.stderr
    assert "Traceback" not in result.stderr


def test_help_lists_visualization_flag() -> None:
    """The viewer is off by default and can be enabled when requested."""
    result = run_cli("--help")
    assert result.returncode == 0
    assert "--visualize" in result.stdout
