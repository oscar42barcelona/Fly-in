"""Regression tests for the map files shipped with Fly-in."""

from pathlib import Path

import pytest

from input.receiver import receiver
from input.validator import Map_

ROOT = Path(__file__).resolve().parents[2]
EASY_MAPS = (
    "01_linear_path.txt",
    "02_simple_fork.txt",
    "03_basic_capacity.txt",
)


@pytest.mark.parametrize("filename", EASY_MAPS)
def test_easy_maps_parse(filename: str) -> None:
    """Each bundled easy map must pass the input parser and schema."""
    path = ROOT / "maps" / "easy" / filename
    lines = path.read_text(encoding="utf-8").splitlines()
    parsed = receiver().slicer(lines)
    model = Map_.model_validate(parsed)
    assert model.NB_DRONES > 0
    assert len(model.CONNECTIONS) > 0


def test_connection_capacity_metadata() -> None:
    """Explicit connection capacities must reach the validated model."""
    path = ROOT / "maps" / "easy" / "03_basic_capacity.txt"
    data = receiver().slicer(path.read_text(encoding="utf-8").splitlines())
    model = Map_.model_validate(data)
    assert model.CONNECTIONS[0].LINK_CAPACITY == 4


def test_negative_coordinate() -> None:
    """Valid signed integer coordinates must not be rejected."""
    path = ROOT / "maps" / "easy" / "02_simple_fork.txt"
    data = receiver().slicer(path.read_text(encoding="utf-8").splitlines())
    model = Map_.model_validate(data)
    assert any(hub.Y == -1 for hub in model.HUBS)


def test_first_declaration_is_nb_drones() -> None:
    """Comments are ignored, but the first declaration must be nb_drones."""
    with pytest.raises(ValueError, match="nb_drones"):
        receiver().slicer(["# map header", "hub: middle 1 1"])
