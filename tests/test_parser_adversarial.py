"""Adversarial CLI and map-parser tests for mandatory evaluation rules."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from input.receiver import receiver
from input.validator import Map_

ROOT = Path(__file__).resolve().parents[1]
VALID = (
    "nb_drones: 1\n"
    "start_hub: start 0 0\n"
    "hub: middle 1 0\n"
    "end_hub: goal 2 0\n"
    "connection: start-middle\n"
    "connection: middle-goal\n"
)


class ParserCliProbe:
    """Run an unfamiliar map through the real CLI with a time limit."""

    def __init__(self, directory: Path) -> None:
        """Store the directory for generated maps."""
        self.directory = directory

    def run(self, text: str) -> subprocess.CompletedProcess[str]:
        """Parse and simulate map text in a separate Python process."""
        path = self.directory / "unseen.txt"
        path.write_text(text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, "cli.py", str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )


INVALID_CASES = [
    ("duplicate-drone-count", "nb_drones: 2\n" + VALID,
     "duplicate nb_drones"),
    ("zero-drones", VALID.replace("nb_drones: 1", "nb_drones: 0"),
     "greater than or equal to 1"),
    ("noninteger-drones", VALID.replace("nb_drones: 1", "nb_drones: many"),
     "valid integer"),
    ("noninteger-coordinate",
     VALID.replace("middle 1 0", "middle 1 x"), "valid integer"),
    ("negative-capacity",
     VALID.replace("hub: middle 1 0",
                   "hub: middle 1 0 [max_drones=-1]"),
     "greater than or equal to 1"),
    ("zero-link-capacity",
     VALID.replace("connection: middle-goal",
                   "connection: middle-goal [max_link_capacity=0]"),
     "greater than or equal to 1"),
    ("unknown-zone-type",
     VALID.replace("hub: middle 1 0",
                   "hub: middle 1 0 [zone=teleport]"),
     "zone"),
    ("duplicate-hub-metadata",
     VALID.replace("hub: middle 1 0",
                   "hub: middle 1 0 [zone=normal zone=priority]"),
     "duplicate hub metadata"),
    ("unknown-hub-metadata",
     VALID.replace("hub: middle 1 0",
                   "hub: middle 1 0 [speed=10]"),
     "unknown hub metadata"),
    ("unclosed-metadata",
     VALID.replace("hub: middle 1 0",
                   "hub: middle 1 0 [color=rainbow"),
     "closing"),
    ("extra-closing-bracket",
     VALID.replace("hub: middle 1 0", "hub: middle 1 0 ]"),
     "stray"),
    ("empty-metadata",
     VALID.replace("hub: middle 1 0", "hub: middle 1 0 []"),
     "empty metadata"),
    ("invalid-link-metadata",
     VALID.replace("connection: middle-goal",
                   "connection: middle-goal [capacity=2]"),
     "invalid connection metadata"),
    ("duplicate-link",
     VALID + "connection: middle-start\n",
     "unique"),
    ("self-link",
     VALID.replace("connection: middle-goal", "connection: middle-middle"),
     "cannot connect to itself"),
    ("unknown-link-target",
     VALID.replace("connection: middle-goal", "connection: middle-missing"),
     "previously defined"),
    ("forward-link-target",
     VALID.replace("hub: middle 1 0\n", "")
     .replace("end_hub: goal 2 0\n",
              "connection: start-middle\n"
              "hub: middle 1 0\n"
              "end_hub: goal 2 0\n")
     .replace("connection: start-middle\nconnection: middle-goal",
              "connection: middle-goal"),
     "previously defined"),
    ("duplicate-hub-name",
     VALID.replace("end_hub: goal 2 0",
                   "hub: middle 2 0\nend_hub: goal 3 0"),
     "unique"),
    ("missing-entry",
     VALID.replace("start_hub: start 0 0\n", ""),
     "Field required"),
    ("missing-exit",
     VALID.replace("end_hub: goal 2 0\n", ""),
     "Field required"),
    ("unrecognized-prefix", VALID + "teleport: middle-goal\n",
     "Unknown prefix"),
]


@pytest.mark.parametrize(
    ("name", "text", "message"),
    INVALID_CASES,
    ids=[case[0] for case in INVALID_CASES],
)
def test_invalid_maps_fail_with_line_and_cause(
    name: str, text: str, message: str, tmp_path: Path
) -> None:
    """Bad maps must not print turns or an uncaught Python traceback."""
    result = ParserCliProbe(tmp_path).run(text)
    assert result.returncode != 0, name
    assert result.stdout == "", name
    assert "Error: " in result.stderr, name
    assert "Line " in result.stderr, result.stderr
    assert message.lower() in result.stderr.lower(), result.stderr
    assert "Traceback" not in result.stderr, result.stderr


@pytest.mark.parametrize("terminal_capacity", ["0", "-2", "invalid"])
def test_entry_and_exit_ignore_capacity_metadata(
    terminal_capacity: str,
    tmp_path: Path,
) -> None:
    """The unlimited terminal zones may specify irrelevant capacities."""
    text = (
        "nb_drones: 2\n"
        f"start_hub: a 0 0 [max_drones={terminal_capacity}]\n"
        f"end_hub: z 1 0 [max_drones={terminal_capacity}]\n"
        "connection: a-z\n"
    )
    result = ParserCliProbe(tmp_path).run(text)
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("-z") == 2


def test_two_zone_map_is_valid(tmp_path: Path) -> None:
    """A direct connection needs no intermediate zone."""
    text = (
        "nb_drones: 1\n"
        "start_hub: start 0 0\n"
        "end_hub: goal 1 0\n"
        "connection: start-goal\n"
    )
    result = ParserCliProbe(tmp_path).run(text)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "D1-goal"


def test_metadata_order_whitespace_and_rainbow() -> None:
    """Allow legal metadata order and non-CSS one-word color values."""
    text = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "hub: middle\t1  0 "
        "[max_drones=2   color=rainbow zone=priority]\n"
        "end_hub: goal 2 0\n"
        "connection: start-middle [max_link_capacity=2]\n"
        "connection: middle-goal\n"
    )
    model = Map_.model_validate(receiver().slicer(text.splitlines()))
    assert model.HUBS[1].COLOR == "rainbow"
    assert model.HUBS[1].MAX_DRONES == 2
    assert model.CONNECTIONS[0].LINK_CAPACITY == 2


def test_parser_reuse_does_not_keep_previous_line_indexes() -> None:
    """Reuse one parser without leaking indices from an earlier map."""
    parser = receiver()
    first = parser.slicer(VALID.splitlines())
    assert Map_.model_validate(first).NB_DRONES == 1
    second = parser.slicer(
        VALID.replace("nb_drones: 1", "nb_drones: 2").splitlines()
    )
    assert Map_.model_validate(second).NB_DRONES == 2
    assert parser.index_nbdrones == [1]
    assert parser.index_hubs == [2, 3, 4]


@pytest.mark.parametrize(
    "text",
    [
        ("nb_drones: 1\nstart_hub: a 0 0\n"
         "end_hub: b 1 0\n"),
        ("nb_drones: 1\nstart_hub: a 0 0\n"
         "hub: wall 1 0 [zone=blocked]\n"
         "end_hub: b 2 0\n"
         "connection: a-wall\nconnection: wall-b\n"),
    ],
    ids=["disconnected", "blocked-only-path"],
)
def test_valid_but_unsolvable_map_fails_cleanly(
    text: str, tmp_path: Path
) -> None:
    """Unsolvable graphs are not syntax errors and must not hang."""
    result = ParserCliProbe(tmp_path).run(text)
    assert result.returncode != 0
    assert "No route exists" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""
