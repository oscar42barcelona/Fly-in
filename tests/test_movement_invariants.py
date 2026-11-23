"""Integration tests for simultaneous movement and restricted transit."""

from pathlib import Path

import pytest

from DroneGen.base import State
from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Planning.base import MovementKind
from DroneGen.Planning.TurnPlanner import TurnPlanner
from input.receiver import receiver
from input.validator import HubType, Map_

ROOT = Path(__file__).resolve().parents[1]


def simulate(
    text: str, max_turns: int = 100
) -> list[list[tuple[int, MovementKind]]]:
    """Execute real planning steps and verify invariants after every turn."""
    model = Map_.model_validate(receiver().slicer(text.splitlines()))
    factory = Factory()
    graph = factory.create_graph(model.HUBS, model.CONNECTIONS)
    start = next(node for node in graph.nodes if node.type == HubType.ENTRY)
    drones = factory.create_drones(model.NB_DRONES, start)
    routes = Algorithm().solve(drones[0], graph, model.NB_DRONES)
    assert routes, "No route generated"

    planner = TurnPlanner()
    turns: list[list[tuple[int, MovementKind]]] = []

    while not all(drone.delivered for drone in drones):
        assert len(turns) < max_turns, "Simulation did not terminate"
        proposed = planner.collect_intents(drones, routes, graph)
        approved = planner.resolve_movements(proposed, graph, routes)
        assert approved, "No movement was approved"
        assert planner.fits_capacities(approved, graph, routes)

        turn = [(intent.drone.id, intent.kind) for intent in approved]
        planner.execute_movements(approved)
        turns.append(turn)

        # Every drone must be stored in exactly one node or connection.
        occupancy = [
            drone
            for node in graph.nodes
            for drone in node.drones
        ] + [
            drone
            for connection in graph.connections
            for drone in connection.drones
        ]
        assert len(occupancy) == len(drones)
        assert set(occupancy) == set(drones)
        assert len(set(occupancy)) == len(occupancy)

        for node in graph.nodes:
            if node.type not in (HubType.ENTRY, HubType.EXIT):
                assert len(node.drones) <= node.capacity, node.name
        for connection in graph.connections:
            assert len(connection.drones) <= connection.capacity
            assert all(
                drone.state == State.TRANSIT
                for drone in connection.drones
            )

    # Each newly started restricted transit must end in the next turn.
    for index, turn in enumerate(turns):
        for drone_id, kind in turn:
            if kind == MovementKind.START_TRANSIT:
                assert index + 1 < len(turns)
                assert (drone_id, MovementKind.END_TRANSIT) in turns[index + 1]

    assert all(drone.delivered for drone in drones)
    return turns


@pytest.mark.parametrize(
    "filename",
    [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/easy/03_basic_capacity.txt",
        "maps/medium/01_dead_end_trap.txt",
        "maps/medium/02_circular_loop.txt",
        "maps/medium/03_priority_puzzle.txt",
        "maps/hard/01_maze_nightmare.txt",
        "maps/hard/02_capacity_hell.txt",
        "maps/hard/03_ultimate_challenge.txt",
    ],
)
def test_bundled_maps_respect_capacity(filename: str) -> None:
    """Bundled maps should complete without invalid simultaneous moves."""
    text = (ROOT / filename).read_text(encoding="utf-8")
    turns = simulate(text)
    print(f"BENCHMARK {filename}: {len(turns)} turns")


def test_restricted_zone_requires_two_turns() -> None:
    """Restricted movements must occupy a connection for one whole turn."""
    text = """
nb_drones: 2
start_hub: start 0 0
hub: restricted 1 0 [zone=restricted max_drones=1]
end_hub: goal 2 0
connection: start-restricted [max_link_capacity=1]
connection: restricted-goal [max_link_capacity=1]
"""
    turns = simulate(text)
    assert (1, MovementKind.START_TRANSIT) in turns[0]
    assert (1, MovementKind.END_TRANSIT) in turns[1]
    assert (2, MovementKind.START_TRANSIT) in turns[1]
    assert (2, MovementKind.END_TRANSIT) in turns[2]
