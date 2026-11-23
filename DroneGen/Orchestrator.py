"""Coordina los turnos de Fly-in mediante TurnPlanner."""

from DroneGen.base import MovementRecord, State, flychestrator
from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Connection, Graph, Node
from DroneGen.Planning.base import MovementIntent, MovementKind
from DroneGen.Planning.TurnPlanner import TurnPlanner


StateKey = tuple[
    int, Node | None, Connection | None, Node | None, State, int, bool
]


class SimulationProgressGuard:
    """Detect a repeated global state before it becomes an infinite loop."""

    def __init__(self) -> None:
        """Record states already visited by the deterministic scheduler."""
        self._seen: set[tuple[StateKey, ...]] = set()

    def observe(self, drones: list[Drone]) -> None:
        """Raise if the same routing and occupancy state recurs."""
        state: tuple[StateKey, ...] = tuple(
            (
                drone.id,
                drone.current_node,
                drone.current_connection,
                drone.headed_to,
                drone.state,
                drone.current_route,
                drone.delivered,
            )
            for drone in drones
        )
        if state in self._seen:
            raise ValueError(
                "Simulation cannot progress: repeated drone state"
            )
        self._seen.add(state)


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
        progress = SimulationProgressGuard()

        while not all(drone.delivered for drone in drones):
            progress.observe(drones)
            # Primero se decide el turno completo, sin modificar el grafo.
            intents = planner.collect_intents(drones, routes, graph)
            approved = planner.resolve_movements(intents, graph, routes)

            if not approved:
                rerouted = self.reassign_stalled_drones(
                    drones, routes, planner, graph
                )
                if rerouted:
                    intents = planner.collect_intents(
                        drones, routes, graph
                    )
                    approved = planner.resolve_movements(
                        intents, graph, routes
                    )
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
    def reassign_stalled_drones(
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        planner: TurnPlanner,
        graph: Graph,
    ) -> int:
        """Choose viable alternative routes when an entire turn is blocked.

        Only change an active drone's path if another precomputed path
        includes its current node and leads to an available next node.
        All proposed movements still pass the normal simultaneous-capacity
        planner before any state is changed.
        """
        changed = 0
        for drone in drones:
            if drone.delivered or drone.state == State.TRANSIT:
                continue
            origin = drone.current_node
            if origin is None:
                continue

            original_route = routes[drone.current_route][1]
            current_index = original_route.index(origin)
            if current_index + 1 >= len(original_route):
                continue
            current_next = original_route[current_index + 1]

            choices: list[tuple[int, int, int]] = []
            for route_id, (cost, path) in routes.items():
                if route_id == drone.current_route:
                    continue
                try:
                    index = path.index(origin)
                except ValueError:
                    continue
                if index + 1 >= len(path):
                    continue
                next_node = path[index + 1]
                if next_node is current_next:
                    continue
                if not next_node.available_node():
                    continue
                connection = planner.find_connection(
                    origin, next_node, graph
                )
                if (
                    connection is None
                    or not connection.available_connection()
                ):
                    continue
                choices.append((len(next_node.drones), cost, route_id))

            if choices:
                _, _, selected_id = min(choices)
                drone.current_route = selected_id
                changed += 1

        return changed

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
