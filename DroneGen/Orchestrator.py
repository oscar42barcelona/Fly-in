"""Coordina los turnos de Fly-in mediante TurnPlanner."""

from DroneGen.base import MovementRecord, flychestrator
from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Graph, Node
from DroneGen.Planning.base import MovementIntent, MovementKind
from DroneGen.Planning.TurnPlanner import TurnPlanner


class orchestrator(flychestrator):
    """Mantiene la interfaz utilizada por formatter_algorithm.py."""

    def plan(
        self,
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        graph: Graph,
    ) -> dict[int, list[MovementRecord]]:
        planner = TurnPlanner()
        self.assign_initial_routes(drones, routes)
        movements_by_turn: dict[int, list[MovementRecord]] = {}
        turn = 0

        while not all(drone.delivered for drone in drones):
            # Primero se decide el turno completo, sin modificar el grafo.
            intents = planner.collect_intents(drones, routes, graph)
            approved = planner.resolve_movements(intents, graph)

            if not approved:
                raise ValueError(
                    "Simulation cannot advance: no movements approved"
                )

            # Todos los movimientos se aplican como un solo turno.
            planner.execute_movements(approved)

            turn += 1
            movements_by_turn[turn] = [
                self.movement_record(intent)
                for intent in approved
            ]

        return movements_by_turn

    @staticmethod
    def assign_initial_routes(
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
    ) -> None:
        """Spread initial traffic across alternative paths.

        Each new assignment increases that route's estimated completion
        time by one turn. Prefer lower-cost routes when scores tie.
        """
        if not routes:
            raise ValueError("No routes available for the simulation")

        allocated = {route_id: 0 for route_id in routes}
        for drone in drones:
            possible = [
                route_id
                for route_id, (_, path) in routes.items()
                if path and path[0] is drone.current_node
            ]
            if not possible:
                raise ValueError("No route starts at the drone's position")

            selected = min(
                possible,
                key=lambda route_id: (
                    routes[route_id][0] + allocated[route_id],
                    routes[route_id][0],
                    route_id,
                ),
            )
            drone.current_route = selected
            allocated[selected] += 1

    @staticmethod
    def movement_record(intent: MovementIntent) -> MovementRecord:
        """Construye un registro para cada movimiento aprobado."""
        if intent.kind == MovementKind.START_TRANSIT:
            connection = intent.connection
            location = (
                f"{connection.node_a.name}-{connection.node_b.name}"
            )
        else:
            location = intent.destination.name

        return MovementRecord(intent.drone.id, intent.drone.state, location)
