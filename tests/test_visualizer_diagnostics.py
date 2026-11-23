"""Check visualizer diagnostics against real simulation records without Pygame."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Orchestrator import orchestrator
from input.receiver import receiver
from input.validator import HubType, Map_
from ui.visualizer.render_tester import _is_end, _is_start, _prepare

ROOT = Path(__file__).resolve().parents[1]


def test_visualizer_recognizes_domain_hub_types() -> None:
    """The Graph uses entry/exit rather than the demo start/end types."""
    assert _is_start(SimpleNamespace(type=HubType.ENTRY))
    assert _is_end(SimpleNamespace(type=HubType.EXIT))
    assert not _is_start(SimpleNamespace(type=HubType.INTERMEDIATE))
    assert not _is_end(SimpleNamespace(type=HubType.INTERMEDIATE))
    # The renderer's historical standalone demo still works.
    assert _is_start(SimpleNamespace(type="start"))
    assert _is_end(SimpleNamespace(type="end"))


@pytest.mark.parametrize(
    "path",
    [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/easy/03_basic_capacity.txt",
        "maps/medium/03_priority_puzzle.txt",
    ],
)
def test_visualizer_accepts_real_turn_history(path: str) -> None:
    """A valid finished simulation should not produce false diagnostics."""
    model = Map_.model_validate(
        receiver().slicer((ROOT / path).read_text(encoding="utf-8").splitlines())
    )
    factory = Factory()
    graph = factory.create_graph(model.HUBS, model.CONNECTIONS)
    start = next(node for node in graph.nodes if node.type == HubType.ENTRY)
    end = next(node for node in graph.nodes if node.type == HubType.EXIT)
    drones = factory.create_drones(model.NB_DRONES, start)
    routes = Algorithm().solve(drones[0], graph, model.NB_DRONES)
    movements = orchestrator().plan(drones, routes, graph)

    # _prepare is pure and does not open a Pygame window.
    snapshots, metadata = _prepare(graph, movements, start_name=None)
    assert metadata["start"] == start.name
    assert not metadata["issues"], [issue.message for issue in metadata["issues"]]
    assert snapshots[-1].turn == max(movements)
    assert len(snapshots[-1].positions) == model.NB_DRONES
    assert set(snapshots[-1].positions.values()) == {end.name}


def test_visualizer_detects_invalid_post_delivery_movement() -> None:
    """After arriving at EXIT, a drone cannot move away unnoticed."""
    from DroneGen.base import MovementRecord, State

    start = SimpleNamespace(name="start", type=HubType.ENTRY, zone="normal", capacity=1)
    end = SimpleNamespace(name="goal", type=HubType.EXIT, zone="normal", capacity=1)
    graph = SimpleNamespace(
        nodes=[start, end],
        connections=[SimpleNamespace(node_a=start, node_b=end, capacity=1)],
    )
    events = {
        1: [MovementRecord(1, State.MOVEMENT, "goal")],
        2: [MovementRecord(1, State.MOVEMENT, "start")],
    }
    _, metadata = _prepare(graph, events, start_name=None)
    assert any("moved after delivery" in issue.message for issue in metadata["issues"])


def test_visualizer_tracks_restricted_transit_without_false_alarm() -> None:
    """The viewer must place a drone on its edge and then at its destination."""
    map_text = """
nb_drones: 1
start_hub: start 0 0
hub: restricted 1 0 [zone=restricted]
end_hub: goal 2 0
connection: start-restricted [max_link_capacity=1]
connection: restricted-goal [max_link_capacity=1]
"""
    model = Map_.model_validate(receiver().slicer(map_text.splitlines()))
    factory = Factory()
    graph = factory.create_graph(model.HUBS, model.CONNECTIONS)
    start = next(node for node in graph.nodes if node.type == HubType.ENTRY)
    drone = factory.create_drones(1, start)[0]
    routes = Algorithm().solve(drone, graph, 1)
    movements = orchestrator().plan([drone], routes, graph)

    snapshots, metadata = _prepare(graph, movements, start_name=None)
    assert not metadata["issues"], [issue.message for issue in metadata["issues"]]
    assert snapshots[1].positions[drone.id] == "edge:start-restricted"
    assert snapshots[2].positions[drone.id] == "restricted"
    assert snapshots[-1].positions[drone.id] == "goal"
