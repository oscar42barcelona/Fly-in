"""Typed, object-oriented simulation service for visual interfaces.

The service depends only on the Fly-in engine and Plotly, not on Streamlit.
It builds one complete simulation and exposes immutable per-turn summaries.
"""

from __future__ import annotations

from dataclasses import dataclass

from plotly.graph_objects import Figure

from DroneGen.base import MovementRecord, State
from DroneGen.Graph.Map import Connection, Node
from input.formatter_algorithm_integrado import SimulationRunner
from input.validator import HubType
from ui.visualizer.plotly_test import plotlyzer
from ui.visualizer.turn_positions import TurnPositions, TurnPositionReplayer


@dataclass(frozen=True)
class TurnMetrics:
    """Counts for a completed turn; turn zero has no waiting drones."""

    delivered: int
    transit: int
    waiting: int


@dataclass(frozen=True)
class SimulationData:
    """Result of a complete simulation, ready for display."""

    figure: Figure
    metrics: dict[int, TurnMetrics]
    total_drones: int


class SimulationService:
    """Prepare a full simulation and its historical drone metrics."""

    def __init__(self, path: str) -> None:
        """Select the map to simulate."""
        self.path = path

    @staticmethod
    def calculate_turn_metrics(
        positions: TurnPositions,
        movements: dict[int, list[MovementRecord]],
    ) -> dict[int, TurnMetrics]:
        """Count drones using historical positions, not final occupancy."""
        result: dict[int, TurnMetrics] = {}

        for turn, places in positions.items():
            moved = {
                record.drone_id
                for record in movements.get(turn, [])
                if record.state != State.STAY
            }
            delivered = sum(
                isinstance(place, Node) and place.type == HubType.EXIT
                for place in places.values()
            )
            transit = sum(
                isinstance(place, Connection)
                for place in places.values()
            )
            waiting = (
                sum(
                    isinstance(place, Node)
                    and place.type != HubType.EXIT
                    and drone_id not in moved
                    for drone_id, place in places.items()
                )
                if turn > 0
                else 0
            )
            result[turn] = TurnMetrics(
                delivered=delivered,
                transit=transit,
                waiting=waiting,
            )

        return result

    def build(self) -> SimulationData:
        """Build metrics and Plotly frames from the shared engine result."""
        result = SimulationRunner(self.path).simulate()
        graph, movements = result.graph, result.movements
        positions = TurnPositionReplayer(graph).replay(movements)
        metrics = self.calculate_turn_metrics(positions, movements)
        figure = plotlyzer(graph).create_visualization(movements)
        return SimulationData(
            figure=figure,
            metrics=metrics,
            total_drones=result.total_drones,
        )
