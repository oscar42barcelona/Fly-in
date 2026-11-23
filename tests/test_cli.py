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


def test_simple_fork_meets_turn_limit() -> None:
    """Four drones must use both branches within the 125% turn budget."""
    result = run_cli("maps/easy/02_simple_fork.txt")
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert len(lines) <= 5, f"Expected at most 5 turns, got {len(lines)}"
    assert sum(line.count("-goal") for line in lines) == 4
    assert any("-path_a" in line for line in lines)
    assert any("-path_b" in line for line in lines)


def test_basic_capacity_meets_turn_limit() -> None:
    """The capacity map must not exceed five simulation turns."""
    result = run_cli("maps/easy/03_basic_capacity.txt")
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert len(lines) <= 5, f"Expected at most 5 turns, got {len(lines)}"
    assert sum(line.count("-goal") for line in lines) == 4


def test_priority_puzzle_meets_turn_limit() -> None:
    """Five drones must finish within seven turns (125% of six)."""
    result = run_cli("maps/medium/03_priority_puzzle.txt")
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert len(lines) <= 7, f"Expected at most 7 turns, got {len(lines)}"
    assert sum(line.count("-goal") for line in lines) == 5
