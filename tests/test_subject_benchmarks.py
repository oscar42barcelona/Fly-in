"""Check all nine mandatory Fly-in maps against the subject benchmarks.

This test exercises the public CLI, not a shortcut through the simulation
engine. Capacity and movement invariants are checked in a separate test.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from input.receiver import receiver
from input.validator import Map_


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SubjectBenchmark:
    """One mandatory map's optimal turns and expected drone count."""

    filename: str
    optimum: int
    drones: int

    @property
    def maximum_turns(self) -> int:
        """Apply the subject's inclusive 125% limit with integer arithmetic."""
        return self.optimum * 5 // 4


BENCHMARKS = (
    SubjectBenchmark("maps/easy/01_linear_path.txt", 4, 2),
    SubjectBenchmark("maps/easy/02_simple_fork.txt", 4, 4),
    SubjectBenchmark("maps/easy/03_basic_capacity.txt", 4, 4),
    SubjectBenchmark("maps/medium/01_dead_end_trap.txt", 8, 5),
    SubjectBenchmark("maps/medium/02_circular_loop.txt", 10, 6),
    SubjectBenchmark("maps/medium/03_priority_puzzle.txt", 6, 5),
    SubjectBenchmark("maps/hard/01_maze_nightmare.txt", 13, 8),
    SubjectBenchmark("maps/hard/02_capacity_hell.txt", 16, 12),
    SubjectBenchmark("maps/hard/03_ultimate_challenge.txt", 26, 15),
)


class SubjectBenchmarkRunner:
    """Validate CLI output and completion time for a subject map."""

    def __init__(self, repository_root: Path) -> None:
        """Store the directory from which Fly-in is normally executed."""
        self.repository_root = repository_root

    def run(self, benchmark: SubjectBenchmark) -> int:
        """Return completed turns after checking delivery and output format."""
        path = self.repository_root / benchmark.filename
        parsed = receiver().slicer(
            path.read_text(encoding="utf-8").splitlines()
        )
        model = Map_.model_validate(parsed)
        assert model.NB_DRONES == benchmark.drones

        try:
            result = subprocess.run(
                [sys.executable, "cli.py", benchmark.filename],
                cwd=self.repository_root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise AssertionError(
                f"{benchmark.filename}: CLI did not finish in 30 seconds"
            ) from error

        assert result.returncode == 0, (
            f"{benchmark.filename}: exit code {result.returncode}\n"
            f"stdout:\n{result.stdout[-1500:]}\n"
            f"stderr:\n{result.stderr[-1500:]}"
        )
        assert not result.stderr.strip(), (
            f"{benchmark.filename}: unexpected stderr: {result.stderr}"
        )

        lines = result.stdout.splitlines()
        assert lines, f"{benchmark.filename}: no simulation turns printed"
        arrivals: Counter[int] = Counter()

        for turn, line in enumerate(lines, start=1):
            moves = line.split()
            assert moves, (
                f"{benchmark.filename}: empty movement line at turn {turn}"
            )
            seen: set[int] = set()
            for movement in moves:
                match = re.fullmatch(r"D([1-9][0-9]*)-(\S+)", movement)
                assert match is not None, (
                    f"{benchmark.filename}, turn {turn}: "
                    f"bad movement {movement!r}"
                )
                drone_id = int(match.group(1))
                destination = match.group(2)
                assert 1 <= drone_id <= benchmark.drones, (
                    f"{benchmark.filename}: unknown drone D{drone_id}"
                )
                assert drone_id not in seen, (
                    f"{benchmark.filename}, turn {turn}: duplicate D{drone_id}"
                )
                seen.add(drone_id)
                if destination == model.END_HUB:
                    arrivals[drone_id] += 1

        assert arrivals == Counter(range(1, benchmark.drones + 1)), (
            f"{benchmark.filename}: not every drone arrives exactly once; "
            f"arrivals={dict(arrivals)}"
        )

        turns = len(lines)
        print(
            f"SUBJECT BENCHMARK {benchmark.filename}: "
            f"{turns} turns, optimum {benchmark.optimum}, "
            f"allowed {benchmark.maximum_turns}, "
            f"delivered {benchmark.drones}/{benchmark.drones}",
            flush=True,
        )
        return turns


@pytest.mark.parametrize(
    "benchmark", BENCHMARKS, ids=lambda benchmark: benchmark.filename
)
def test_nine_mandatory_maps_within_125_percent(
    benchmark: SubjectBenchmark,
) -> None:
    """Require every subject map to finish within its individual limit."""
    turns = SubjectBenchmarkRunner(ROOT).run(benchmark)
    assert turns <= benchmark.maximum_turns, (
        f"{benchmark.filename}: {turns} turns exceeds "
        f"the required limit {benchmark.maximum_turns} "
        f"(optimum {benchmark.optimum})"
    )
