from input.validator import Zone, HubType
from .Drone import Drone


class Node:
    def __init__(self, name: str,
                x: int, y: int,
                hub_type: HubType,
                zone: Zone,
                color: str,
                max_drones: int
                ):
        self.name = name
        self.x = x
        self.y = y
        self.type = hub_type
        self.zone = zone
        self.COLOR = color
        self.capacity = max_drones
        self.drones: list[Drone]
        self.queueing_drones: list[Drone]

    def available_node(self, drone: Drone) -> bool:
        """registrar la presencia de un dron en el nodo."""

        if len(self.drones) >= self.capacity:
            return False

        return True

    def queueing_drones(self, drone: Drone) -> list[Drone]:
         self.queueing_drones.append(drone)
        
    def enter_drone(self, drone: Drone) -> bool:
        """registrar la presencia de un dron en el nodo."""

        if available_drone(Drone) is False:
            return False

        if drone in self.queueing_drones:
            self.queueing_drones.remove(drone)

        #pendiente precisar duplicados, 
        #nodos bloqueados, 
        #restricciones y tratamiento de inicio/final.
        
        self.drones.append(drone)

        return True

    def exit_drone(self, drone: Drone) -> bool:
        pass

        #pendiente determinar qué ocurre si no está presente.

        # o bien self.drones.popleft() o quitar el que me digan


class Connection:
    def __init__(self, node_a: Node, 
                 node_b: Node,
                 max_link_capacity: int):
        self.node_a = node_a
        self.node_b = node_b
        self.capacity = max_link_capacity
        self.drones: list[Drone]
            
    def enter_connection(self, drone: Drone) -> bool:

        if len(self.drones) == self.capacity:
            return False

        #impedir duplicados; detalle de fallo pendiente.

        self.drones.append(drone)
        return True

    def exit_connection(self, drone) -> bool:
        ...
        #pendiente determinar qué ocurre si no está presente.

        # o bien self.drones.popleft() o quitar el que me digan

    def get_midpoint(self) -> (int, int):
        pass
        # obtener un punto representativo en la mitad 
        #de los extremos para representación visual.
        #Errores: no se han tratado casos especiales.
        #Ejemplo: extremos (0, 0) y (4, 2) dan (2, 1).

        
class Graph:
    def __init__(self, nodes: list[Node],
                connections: list[Connection]):
        self.nodes = nodes
        self.connections = connections

    def get_connections(self, node: Node) -> list[Node]:
        list_nodes: list[Node] = []

        for connection in self.connections:
            if node == connection.node_a:
                list_nodes.append(connection.node_b)
            elif node == connection.node_b:
                list_nodes.append(connection.node_a)
        return list_nodes
