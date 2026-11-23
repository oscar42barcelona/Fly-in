"""Unseen but valid graphs exercise routing beyond the nine shipped maps."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


class UnseenMapFactory:
    """Build small custom maps with predictable legal topologies."""

    @staticmethod
    def direct(drones: int) -> str:
        """Provide a two-zone topology with an unlimited exit."""
        return (
            f"nb_drones: {drones}\n"
            "start_hub: entry 0 0\n"
            "end_hub: finish 1 0\n"
            "connection: entry-finish\n"
        )

    @staticmethod
    def restricted(drones: int) -> str:
        """Send drones through a capacity-one restricted crossing."""
        return (
            f"nb_drones: {drones}\n"
            "start_hub: entry 0 0\n"
            "hub: tunnel 1 0 [zone=restricted max_drones=1]\n"
            "end_hub: finish 2 0\n"
            "connection: entry-tunnel [max_link_capacity=1]\n"
            "connection: tunnel-finish\n"
        )

    @staticmethod
    def priority_detour(drones: int) -> str:
        """Expose a parallel route, a cycle, and an inaccessible node."""
        return (
            f"nb_drones: {drones}\n"
            "start_hub: entry 0 0\n"
            "hub: fast 1 0 [zone=priority max_drones=2]\n"
            "hub: slow 1 1 [max_drones=2]\n"
            "hub: shared 2 0 [max_drones=2]\n"
            "hub: wall 2 1 [zone=blocked]\n"
            "end_hub: finish 3 0\n"
            "connection: entry-fast\n"
            "connection: entry-slow\n"
            "connection: fast-shared [max_link_capacity=2]\n"
            "connection: slow-shared [max_link_capacity=2]\n"
            "connection: shared-finish [max_link_capacity=2]\n"
            "connection: slow-wall\n"
            "connection: wall-finish\n"
        )


@pytest.mark.parametrize(
    ("map_text", "drones"),
    [
        (UnseenMapFactory.direct(1), 1),
        (UnseenMapFactory.direct(40), 40),
        (UnseenMapFactory.restricted(1), 1),
        (UnseenMapFactory.restricted(12), 12),
        (UnseenMapFactory.priority_detour(8), 8),
    ],
    ids=[
        "two-zones", "forty-drones", "restricted-single",
        "restricted-queue", "priority-detour-cycle",
    ],
)
def test_unseen_valid_maps_deliver_every_drone(
    map_text: str, drones: int, tmp_path: Path
) -> None:
    """The real CLI must terminate and deliver all drones exactly once."""
    path = tmp_path / "unseen_valid.txt"
    path.write_text(map_text, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "cli.py", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not result.stderr
    lines = result.stdout.splitlines()
    assert lines

    arrivals: list[int] = []
    for line in lines:
        seen: set[int] = set()
        for part in line.split():
            match = re.fullmatch(r"D([1-9][0-9]*)-([^ ]+)", part)
            assert match is not None, part
            drone_id = int(match.group(1))
            assert drone_id not in seen, line
            seen.add(drone_id)
            if match.group(2) == "finish":
                arrivals.append(drone_id)

    assert sorted(arrivals) == list(range(1, drones + 1))


def test_cli_reads_mixed_comment_and_metadata_order(
    tmp_path: Path,
) -> None:
    """The first meaningful line may follow a comment block."""
    path = tmp_path / "commented.txt"
    path.write_text(
        "# Fly-in map\n"
        "\n"
        "nb_drones: 1 # one drone\n"
        "start_hub: entry 0 0 [color=green]\n"
        "hub: bridge 1 0 [color=rainbow zone=priority]\n"
        "end_hub: finish 2 0 [color=red]\n"
        "connection: entry-bridge # normal connection\n"
        "connection: bridge-finish\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "cli.py", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "D1-bridge", "D1-finish"
    ]
