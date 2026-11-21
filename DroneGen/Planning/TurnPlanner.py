"""Planificacion y ejecucion simultanea de movimientos de drones."""

from DroneGen.base import State
from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Connection, Graph, Node
from DroneGen.Planning.base import MovementIntent, MovementKind, BaseTurnPlanner
from input.validator import Zone


class TurnPlanner(BaseTurnPlanner):
    """Decide un turno usando ocupaciones conjuntas, sin mover al evaluar."""

    def collect_intents(
        self,
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        graph: Graph,
    ) -> list[MovementIntent]:
        """Recoge un movimiento propuesto por cada dron activo."""
        intents: list[MovementIntent] = []

        for drone in drones:
            if drone.delivered:
                continue

            if drone.state == State.TRANSIT:
                if drone.current_connection is None or drone.headed_to is None:
                    raise ValueError("Invalid transit state")
                intents.append(
                    MovementIntent(
                        drone=drone,
                        origin=None,
                        destination=drone.headed_to,
                        connection=drone.current_connection,
                        kind=MovementKind.END_TRANSIT,
                    )
                )
                continue

            origin = drone.current_node
            if origin is None:
                raise ValueError("Drone has no current node")

            _, route = routes[drone.current_route]
            try:
                index = route.index(origin)
            except ValueError as exc:
                raise ValueError("Drone is not in its assigned route") from exc

            if index + 1 == len(route):
                continue

            destination = route[index + 1]
            connection = self.find_connection(origin, destination, graph)
            if connection is None:
                raise ValueError("Route contains disconnected nodes")

            kind = (
                MovementKind.START_TRANSIT
                if destination.zone == Zone.RESTRICTED
                else MovementKind.NORMAL
            )
            intents.append(
                MovementIntent(
                    drone=drone,
                    origin=origin,
                    destination=destination,
                    connection=connection,
                    kind=kind,
                )
            )

        return intents

    def find_connection(
        self, origin: Node, destination: Node, graph: Graph
    ) -> Connection | None:
        """Localiza la conexion bidireccional entre dos nodos."""
        for connection in graph.connections:
            if (
                connection.node_a is origin
                and connection.node_b is destination
            ) or (
                connection.node_b is origin
                and connection.node_a is destination
            ):
                return connection
        return None

    def validate_intents(
        self, intents: list[MovementIntent], graph: Graph
    ) -> None:
        """Rechaza propuestas incompatibles con el estado real del grafo."""
        seen: set[Drone] = set()
        ending: set[Drone] = set()

        for intent in intents:
            drone = intent.drone
            if drone in seen:
                raise ValueError("Drone has multiple intents")
            seen.add(drone)

            if drone.delivered:
                raise ValueError("Delivered drone cannot move")
            if intent.destination not in graph.nodes:
                raise ValueError("Unknown destination")
            if intent.destination.zone == Zone.BLOCKED:
                raise ValueError("Movement into blocked zone")
            if intent.connection not in graph.connections:
                raise ValueError("Unknown connection")

            connection = intent.connection
            if intent.kind == MovementKind.END_TRANSIT:
                if (
                    intent.origin is not None
                    or drone.state != State.TRANSIT
                    or drone.current_node is not None
                    or drone.current_connection is not connection
                    or drone.headed_to is not intent.destination
                    or drone not in connection.drones
                ):
                    raise ValueError("Invalid transit arrival")
                if intent.destination not in (
                    connection.node_a, connection.node_b
                ):
                    raise ValueError("Transit destination not connected")
                ending.add(drone)
                continue

            origin = intent.origin
            if (
                origin is None
                or origin not in graph.nodes
                or drone.current_node is not origin
                or drone.current_connection is not None
                or drone.state == State.TRANSIT
                or drone not in origin.drones
            ):
                raise ValueError("Invalid movement origin")
            if self.find_connection(origin, intent.destination, graph) is not connection:
                raise ValueError("Movement uses an incorrect connection")
            expected_kind = (
                MovementKind.START_TRANSIT
                if intent.destination.zone == Zone.RESTRICTED
                else MovementKind.NORMAL
            )
            if intent.kind != expected_kind:
                raise ValueError("Movement kind does not match destination")

        # Todo dron que ocupa una conexion debe llegar en este turno.
        for connection in graph.connections:
            for drone in connection.drones:
                if drone not in ending:
                    raise ValueError("Missing mandatory transit arrival")

    def find_capacity_conflicts(
        self, intents: list[MovementIntent], graph: Graph
    ) -> tuple[list[Node], list[Node], list[Connection]]:
        """Devuelve nodos llenos, nodos negativos y conexiones invalidas."""
        occupancy = {node: len(node.drones) for node in graph.nodes}
        link_usage = {
            connection: len(connection.drones)
            for connection in graph.connections
        }
        #Aqui actualizamos los drones que estaran en las conexiones o nodos.
        for intent in intents:
            if intent.kind == MovementKind.END_TRANSIT:
                link_usage[intent.connection] -= 1
                occupancy[intent.destination] += 1
            else:
                origin = intent.origin
                if origin is None:
                    raise ValueError("Movement has no origin")
                occupancy[origin] -= 1
                link_usage[intent.connection] += 1
                if intent.kind == MovementKind.NORMAL:
                    occupancy[intent.destination] += 1

        overloaded_nodes = [
            node for node in graph.nodes
            if node.type not in ("entry", "exit")
            and occupancy[node] > node.capacity
        ]
        negative_nodes = [
            node for node in graph.nodes if occupancy[node] < 0
        ]
        bad_connections = [
            connection for connection in graph.connections
            if link_usage[connection] < 0
            or link_usage[connection] > connection.capacity
        ]
        return overloaded_nodes, negative_nodes, bad_connections

    def find_reservation_conflicts(
        self, intents: list[MovementIntent], graph: Graph
    ) -> list[Node]:
        """Reserva plazas para los START_TRANSIT del siguiente turno.

        Criterio conservador: ninguna salida futura libera una reserva.
        """
        occupancy = {node: len(node.drones) for node in graph.nodes}
        #primer bucle movimientos de ette turno
        for intent in intents:
            if intent.kind == MovementKind.END_TRANSIT:
                occupancy[intent.destination] += 1
            else:
                origin = intent.origin
                if origin is None:
                    raise ValueError("Movement has no origin")
                occupancy[origin] -= 1
                if intent.kind == MovementKind.NORMAL:
                    occupancy[intent.destination] += 1
        #reserva para los restricted
        for intent in intents:
            if intent.kind == MovementKind.START_TRANSIT:
                occupancy[intent.destination] += 1
        #devuelvo solo los nodos en los que se prevee probblma de ocupacion
        return [
            node for node in graph.nodes
            if node.type not in ("entry", "exit")
            and occupancy[node] > node.capacity
        ]

    def fits_capacities(
        self, intents: list[MovementIntent], graph: Graph
    ) -> bool:
        """Comprueba capacidades actuales y reservas de llegadas futuras."""
        overloaded, negative, bad_links = self.find_capacity_conflicts(
            intents, graph
        )
        reservations = self.find_reservation_conflicts(intents, graph)
        return not (overloaded or negative or bad_links or reservations)

    def resolve_movements(
        self, intents: list[MovementIntent], graph: Graph
    ) -> list[MovementIntent]:
        """Retira movimientos opcionales hasta encontrar un turno valido.

        La seleccion es voraz; no garantiza el minimo global de turnos.
        """
        self.validate_intents(intents, graph)
        #Esta línea crea una nueva lista con los mismos elementos que intents.
        approved = list(intents)

        while True:
            overloaded, negative, bad_links = self.find_capacity_conflicts(
                approved, graph
            )

            if negative:
                raise RuntimeError(
                    f"Negative occupancy detected in nodes: "
                    f"{[node.name for node in negative]}")

            reservations = self.find_reservation_conflicts(approved, graph)
            if not (overloaded or negative or bad_links or reservations):
                return approved

            removable: MovementIntent | None = None

            # Entrada en un nodo que termina por encima de su capacidad.
            for node in overloaded:
                removable = next(
                    (
                        intent for intent in reversed(approved)
                        if intent.kind == MovementKind.NORMAL
                        and intent.destination is node
                    ),
                    None,
                )
                if removable is not None:
                    break

            # Demasiados drones usan una conexion durante el mismo turno.
            if removable is None:
                for connection in bad_links:
                    removable = next(
                        (
                            intent for intent in reversed(approved)
                            if intent.kind != MovementKind.END_TRANSIT
                            and intent.connection is connection
                        ),
                        None,
                    )
                    if removable is not None:
                        break

            # Una llegada futura no tiene plaza reservada.
            if removable is None:
                for node in reservations:
                    removable = next(
                        (
                            intent for intent in reversed(approved)
                            if intent.kind == MovementKind.START_TRANSIT
                            and intent.destination is node
                        ),
                        None,
                    )
                    if removable is None:
                        removable = next(
                            (
                                intent for intent in reversed(approved)
                                if intent.kind == MovementKind.NORMAL
                                and intent.destination is node
                            ),
                            None,
                        )
                    if removable is not None:
                        break

            if removable is None:
                raise ValueError("No feasible movement set for this turn")
            approved.remove(removable)

    def execute_movements(self, approved: list[MovementIntent]) -> None:
        """Aplica un conjunto previamente aprobado sin decisiones intermedias."""
        # Fase 1: liberar los nodos de origen y las conexiones finalizadas.
        for intent in approved:
            if intent.kind == MovementKind.END_TRANSIT:
                intent.connection.drones.remove(intent.drone)
            else:
                origin = intent.origin
                if origin is None:
                    raise ValueError("Movement has no origin")
                origin.drones.remove(intent.drone)

        # Fase 2: realizar llegadas. Todas las salidas ya estan aplicadas.
        for intent in approved:
            if intent.kind not in (MovementKind.NORMAL, MovementKind.END_TRANSIT):
                continue
            drone = intent.drone
            destination = intent.destination
            destination.drones.append(drone)
            if intent.kind == MovementKind.END_TRANSIT:
                drone.current_connection = None
                drone.headed_to = None
            drone.move_to_node(destination)

        # Fase 3: iniciar conexiones restringidas que duran hasta el proximo turno.
        for intent in approved:
            if intent.kind != MovementKind.START_TRANSIT:
                continue
            intent.connection.drones.append(intent.drone)
            intent.drone.start_restricted_transit(
                intent.connection, intent.destination
            )
