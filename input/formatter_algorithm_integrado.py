"""Object-oriented simulation entry point with a compatible main wrapper."""

from __future__ import annotations

from DroneGen.base import MovementRecord
from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Graph.Map import Graph
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Orchestrator import orchestrator
from input.receiver import receiver
from input.validator import HubType


class SimulationRunner:
    """Coordinate validated input, graph construction and turn output."""

    def __init__(
        self, map_path: str | None = None, visualize: bool = False
    ) -> None:
        """Remember the requested input file and visualization mode."""
        self.map_path = map_path
        self.visualize = visualize

    def _simulate(self) -> tuple[Graph, dict[int, list[MovementRecord]]]:
        """Build a validated graph and calculate all scheduled movements."""
        model = receiver(self.map_path).load()
        factory = Factory()
        graph = factory.create_graph(
            hubs=model.HUBS,
            connections=model.CONNECTIONS,
        )

        start = next(
            (node for node in graph.nodes if node.name == model.START_HUB),
            None,
        )
        if start is None or start.type != HubType.ENTRY:
            raise ValueError("Start zone does not match the map entry")

        drones = factory.create_drones(
            nb_drones=model.NB_DRONES,
            start_node=start,
        )
        if not drones:
            raise ValueError("The simulation has no drones")

        routes = Algorithm().solve(drones[0], graph, model.NB_DRONES)
        movements = orchestrator().plan(drones, routes, graph)
        return graph, movements

    def run(self) -> None:
        """Print movements and optionally export the Plotly visualization."""
        graph, movements = self._simulate()
        for records in movements.values():
            print(" ".join(
                f"D{record.drone_id}-{record.location}"
                for record in records
            ))

        if self.visualize:
            from ui.visualizer.plotly_test import plotlyzer

            figure = plotlyzer(graph).create_visualization(movements)
            figure.write_html("flyin_preview.html", auto_open=False)


def main(map_path: str | None = None, visualize: bool = False) -> None:
    """Preserve the existing public entry point for integrations."""
    SimulationRunner(map_path, visualize).run()


if __name__ == "__main__":
    main()
