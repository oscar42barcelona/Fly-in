"""Temporary diagnostics for two failing subject benchmarks."""

from __future__ import annotations

from pathlib import Path

import pytest

from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Graph
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Orchestrator import orchestrator
from DroneGen.Planning.TurnPlanner import TurnPlanner
from input.receiver import receiver
from input.validator import HubType, Map_

ROOT = Path(__file__).resolve().parents[1]


class RoutingDiagnostic:
    """Report initial path assignment and where capacity planning stalls."""

    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        """Keep the actual graph and its drone collection."""
        self.graph = graph
        self.drones = drones

    def report(self, max_turns: int = 35) -> None:
        """Print assigned paths and each turn's selected movements."""
        routes = Algorithm().solve(
            self.drones[0], self.graph, len(self.drones)
        )
        print("ROUTES", flush=True)
        for route_id, (cost, nodes) in routes.items():
            names = " > ".join(node.name for node in nodes)
            print(f"  route {route_id}: cost={cost}, {names}", flush=True)

        orchestrator.assign_initial_routes(self.drones, routes)
        print(
            "ASSIGNMENT",
            [(d.id, d.current_route) for d in self.drones],
            flush=True,
        )
        planner = TurnPlanner()
        for turn in range(1, max_turns + 1):
            if all(d.delivered for d in self.drones):
                print(f"FINISHED {turn - 1} turns", flush=True)
                return

            intents = planner.collect_intents(
                self.drones, routes, self.graph
            )
            try:
                approved = planner.resolve_movements(intents, self.graph, routes)
            except (ValueError, RuntimeError) as error:
                print(f"TURN {turn} PLANNING ERROR: {error}", flush=True)
                return

            print(
                f"TURN {turn}: approved={len(approved)}/{len(intents)} ",
                [
                    (intent.drone.id, intent.kind.name,
                     intent.destination.name)
                    for intent in approved
                ],
                flush=True,
            )

            if not approved:
                print(
                    "STALLED POSITIONS",
                    [
                        (d.id, d.current_route,
                         d.current_node.name if d.current_node else None,
                         d.headed_to.name if d.headed_to else None)
                        for d in self.drones if not d.delivered
                    ],
                    flush=True,
                )
                for intent in intents:
                    print(
                        "  rejected candidate",
                        intent.drone.id, intent.kind.name,
                        intent.destination.name,
                        flush=True,
                    )
                print(
                    "OCCUPIED",
                    [
                        (node.name, node.capacity,
                         [drone.id for drone in node.drones])
                        for node in self.graph.nodes if node.drones
                    ],
                    flush=True,
                )
                return

            planner.execute_movements(approved)
        print(f"LIMIT: did not finish after {max_turns} turns", flush=True)


@pytest.mark.parametrize(
    "filename",
    [
        "maps/medium/02_circular_loop.txt",
        "maps/hard/02_capacity_hell.txt",
    ],
)
def test_print_current_routing_diagnostics(filename: str) -> None:
    """Show the current routes without changing any implementation."""
    model = Map_.model_validate(receiver().slicer(
        (ROOT / filename).read_text(encoding="utf-8").splitlines()
    ))
    factory = Factory()
    graph = factory.create_graph(model.HUBS, model.CONNECTIONS)
    start = next(
        node for node in graph.nodes if node.type == HubType.ENTRY
    )
    drones = factory.create_drones(model.NB_DRONES, start)
    print(f"DIAGNOSIS: {filename}", flush=True)
    RoutingDiagnostic(graph, drones).report()
