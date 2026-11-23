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


def test_capacity_info_prints_usage_each_turn() -> None:
    """Capacity mode supplements, but does not replace, the movement output."""
    map_file = "maps/easy/01_linear_path.txt"
    baseline = run_cli(map_file)
    detailed = run_cli("--capacity-info", map_file)
    assert baseline.returncode == detailed.returncode == 0, detailed.stderr

    movements = baseline.stdout.strip().splitlines()
    lines = detailed.stdout.strip().splitlines()
    # The map has 4 nodes and 3 connections: eight lines per turn.
    assert len(lines) == len(movements) * 8
    for turn, move in enumerate(movements):
        block = lines[turn * 8:(turn + 1) * 8]
        assert block[0] == move
        assert len([line for line in block if line.startswith("Zone ")]) == 4
        assert len([line for line in block if line.startswith("Connection ")]) == 3
    assert "Zone start: 1/unlimited drones" in lines[1:8]
    assert "Zone waypoint1: 1/1 drones" in lines[1:8]
    assert "Connection start-waypoint1: 1/1 capacity used" in lines[1:8]
    assert "Zone goal: 2/unlimited drones" in lines[-7:]


def test_capacity_info_counts_restricted_transit(tmp_path: Path) -> None:
    """A transit occupies its connection before arriving at the zone."""
    path = tmp_path / "restricted.txt"
    path.write_text(
        "nb_drones: 1\n"
        "start_hub: start 0 0\n"
        "hub: restricted 1 0 [zone=restricted]\n"
        "end_hub: goal 2 0\n"
        "connection: start-restricted [max_link_capacity=1]\n"
        "connection: restricted-goal [max_link_capacity=1]\n",
        encoding="utf-8",
    )
    result = run_cli("--capacity-info", str(path))
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "D1-start-restricted"
    assert "Zone restricted: 0/1 drones" in lines[1:6]
    assert "Connection start-restricted: 1/1 capacity used" in lines[1:6]
    assert "Zone restricted: 1/1 drones" in lines[7:12]
    assert "Connection start-restricted: 0/1 capacity used" in lines[7:12]


def test_help_lists_capacity_info_flag() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "--capacity-info" in result.stdout
