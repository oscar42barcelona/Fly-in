"""Punto de entrada de Fly-in: entrada, rutas, turnos y visualizacion."""

from input.receiver import receiver
from input.validator import HubType, Map_
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Orchestrator import orchestrator
from ui.visualizer.render_tester import launch


def main(
    map_path: str | None = None,
    visualize: bool = False,
    capacity_info: bool = False,
) -> None:
    """Parse a map, schedule its drones, and print the turn-by-turn moves."""
    raw_map = receiver(map_path).Process()
    if not raw_map:
        raise ValueError("No se ha recibido un mapa")

    model = Map_.model_validate(raw_map, extra="forbid")
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
        raise ValueError("start_hub no corresponde a un nodo de entrada")

    drones = factory.create_drones(
        nb_drones=model.NB_DRONES,
        start_node=start,
    )
    if not drones:
        raise ValueError("No se han creado drones")

    routes = Algorithm().solve(drones[0], graph, model.NB_DRONES)
    planner = orchestrator()
    movements = planner.plan(drones, routes, graph)

    for turn, records in movements.items():
        moves = " ".join(
            f"D{record.drone_id}-{record.location}"
            for record in records
        )
        print(moves)

        if capacity_info:
            zones, links = planner.capacity_by_turn[turn]
            for node in graph.nodes:
                limit = (
                    "unlimited"
                    if node.type in (HubType.ENTRY, HubType.EXIT)
                    else str(node.capacity)
                )
                print(f"Zone {node.name}: {zones[node]}/{limit} drones")
            for connection in graph.connections:
                name = f"{connection.node_a.name}-{connection.node_b.name}"
                print(
                    f"Connection {name}: "
                    f"{links[connection]}/{connection.capacity} capacity used"
                )

    if visualize:
        launch(graph, movements, start_name=start.name)


if __name__ == "__main__":
    main()
