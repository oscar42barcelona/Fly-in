"""Regression tests for deterministic simulation-cycle detection."""

from __future__ import annotations

import pytest

from DroneGen.Graph.MapFactory import Factory
from DroneGen.Orchestrator import SimulationProgressGuard
from input.validator import Hub, HubType


def test_repeat_state_is_detected_before_an_infinite_loop() -> None:
    """Identical drone positions and route assignments cannot repeat."""
    factory = Factory()
    start = factory.create_node(
        Hub(name="start", x=0, y=0, type=HubType.ENTRY)
    )
    drone = factory.create_drone(start)
    guard = SimulationProgressGuard()

    guard.observe([drone])
    with pytest.raises(ValueError, match="repeated drone state"):
        guard.observe([drone])


def test_a_real_progression_is_not_mistaken_for_a_cycle() -> None:
    """Movement changes the observable state and is permitted."""
    factory = Factory()
    start = factory.create_node(
        Hub(name="start", x=0, y=0, type=HubType.ENTRY)
    )
    goal = factory.create_node(
        Hub(name="goal", x=1, y=0, type=HubType.EXIT)
    )
    drone = factory.create_drone(start)
    guard = SimulationProgressGuard()

    guard.observe([drone])
    drone.move_to_node(goal)
    guard.observe([drone])
    with pytest.raises(ValueError, match="repeated drone state"):
        guard.observe([drone])
