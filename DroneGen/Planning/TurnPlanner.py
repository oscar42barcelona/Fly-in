from DroneGen.base import State
from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Node, Graph, Connection
from DroneGen.Planning.MovementIntent import MovementIntent


class TurnPlanner:

    def collect_intents(
        self,
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        graph: Graph
    ) -> list[MovementIntent]:
        """Su función es recopilar los movimientos que los drones quieren realizar durante un turno, sin ejecutarlos todavía."""

        intents: list[MovementIntent] = []

        for drone in drones:
            if drone.delivered:
                continue
            #En el caso de que este en el enlace, debe de completarse el turno hacia el nodo.
            if drone.state == State.TRANSIT:
                if (
                    drone.current_connection is None
                    or drone.headed_to is None
                ):
                    raise ValueError("Invalid transit state")

                intents.append(
                    MovementIntent(
                        drone=drone,
                        origin=None,
                        destination=drone.headed_to,
                        connection=drone.current_connection
                    )
                )
                continue

            current_node = drone.current_node

            if current_node is None:
                raise ValueError("Drone has no current node")

            _, route = routes[drone.current_route]
            #para saber posicion metodo index.
            try:
                index = route.index(current_node)
            except ValueError as exc:
                raise ValueError(
                    "Drone is not in its assigned route"
                ) from exc
            #si estamos en el nodo final no hay que proponer nada
            if index + 1 >= len(route):
                continue

            next_node = route[index + 1]
            #buscamos la conexion
            connection = self.find_connection(
                current_node,
                next_node,
                graph
            )

            if connection is None:
                raise ValueError(
                    "Route contains disconnected nodes"
                )
            #proponemos el siguiente nodo al que avanzar
            intents.append(
                MovementIntent(
                    drone=drone,
                    origin=current_node,
                    destination=next_node,
                    connection=connection
                )
            )

        return intents

    def find_connection(
        self,
        origin: Node,
        destination: Node,
        graph: Graph
    ) -> Connection | None:

        for connection in graph.connections:
            if (
                connection.node_a == origin
                and connection.node_b == destination
            ) or (
                connection.node_b == origin
                and connection.node_a == destination
            ):
                return connection

        return None

    def resolve_movements(
        self,
        intents: list[MovementIntent],
        graph: Graph
        ) -> list[MovementIntent]:
        ...

    def execute_movements(
        self,
        approved: list[MovementIntent]
    ) -> None:
    ...
    ...
