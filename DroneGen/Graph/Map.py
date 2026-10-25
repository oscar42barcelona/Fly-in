#import Zone , drones, queue


class Node:
    def __init__(self, name: str,
                x: int, y: int,
                zone_type: Zone,
                max_drones: int
                )
        self.name = name
        self.x = x
        self.y = y
        self.zone = zone_type
        self.capacity = max_drones
        self.drones: list[Drone]

    def enter_node(self, drone: Drone) -> bool:
        """registrar la presencia de un dron en el nodo."""

        if len(self.drones) == self.capacity
            return False
        #pendiente precisar duplicados, 
        #nodos bloqueados, 
        #restricciones y tratamiento de inicio/final.

        self.drones.append(drone)
        return True

    def exit_node(self, drone: Drone) -> bool:

        #pendiente determinar qué ocurre si no está presente.

        # o bien self.drones.popleft() o quitar el que me digan


class Connection:
    def __init__(self, node_a: Node, 
                 node_b: Node,
                 max_link_capacity: int)
        self.node_a = node_a
        self.node_b = node_b
        self.capacity = max_link_capacity
        self.drones: list[Drone]
            
    def enter_connection(self, drone: Drone): bool:

        if len(self.drones) == self.capacity
            return False

        #impedir duplicados; detalle de fallo pendiente.

        self.drones.append(drone)
        return True

    def exit_connection(self, drone) -> bool:
        #pendiente determinar qué ocurre si no está presente.

        # o bien self.drones.popleft() o quitar el que me digan

    def get_midpoint(self) -> (int, int)
        # obtener un punto representativo en la mitad 
        #de los extremos para representación visual.
        #Errores: no se han tratado casos especiales.
        #Ejemplo: extremos (0, 0) y (4, 2) dan (2, 1).


class Drone:
    def __init__(self, id_: int,
                start_node: Node)
        self.id = id_
        self.current_node = start_node
        self.current_connection: Connection | None = None
        self.headed_to: Node | None = None
        self.delivered: bool = False

    #nos quedamos en el 4.3 move_to...
