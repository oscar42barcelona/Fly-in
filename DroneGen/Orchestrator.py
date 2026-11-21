"""Coordina los turnos de Fly-in mediante TurnPlanner."""

from DroneGen.base import MovementRecord, flychestrator
from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Graph, Node
from DroneGen.Planning.MovementIntent import MovementIntent, MovementKind
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
