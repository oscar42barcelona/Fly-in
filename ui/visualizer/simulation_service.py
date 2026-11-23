"""Prepare simulation data and per-turn metrics for the visual interface.

No Streamlit dependency belongs in this service: it can also be tested and
reused by other consumers of the Fly-in simulation.
"""

from __future__ import annotations

from dataclasses import dataclass

from plotly.graph_objects import Figure

from DroneGen.base import MovementRecord, State
from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Graph.Map import Connection, Node
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Orchestrator import orchestrator
from input.receiver import receiver
from input.validator import HubType
from ui.visualizer.plotly_test import plotlyzer
from ui.visualizer.turn_positions import TurnPositions, replay_turns


@dataclass(frozen=True)
class TurnMetrics:
    """End-of-turn drone counts; turn zero has no waiting drones."""

    delivered: int
    transit: int
    waiting: int


def calculate_turn_metrics(
    positions: TurnPositions,
    movements: dict[int, list[MovementRecord]],
) -> dict[int, TurnMetrics]:
    """Calculate counts from historical snapshots, not final graph occupancy."""
    metrics: dict[int, TurnMetrics] = {}

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
        metrics[turn] = TurnMetrics(
            delivered=delivered,
            transit=transit,
            waiting=waiting,
        )

    return metrics


def build_simulation(
    path: str,
) -> tuple[Figure, dict[int, TurnMetrics], int]:
    """Run Fly-in once and return the animated figure, metrics and drone count."""
    model = receiver(path).Process()
    if model is None:
        raise ValueError("No se ha podido cargar el mapa")

    factory = Factory()
    graph = factory.create_graph(
        hubs=model.HUBS,
        connections=model.CONNECTIONS,
    )
    start = next(
        (node for node in graph.nodes if node.type == HubType.ENTRY),
        None,
    )
    if start is None:
        raise ValueError("No existe un nodo de entrada")

    drones = factory.create_drones(model.NB_DRONES, start)
    routes = Algorithm().solve(drones[0], graph, model.NB_DRONES)
    movements = orchestrator().plan(drones, routes, graph)

    positions = replay_turns(graph, movements)
    metrics = calculate_turn_metrics(positions, movements)
    figure = plotlyzer(graph).create_visualization(movements)

    return figure, metrics, len(drones)
