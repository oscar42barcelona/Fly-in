from .base import flychestrator
from Graph.Map import Node, Connection
from Graph.Drone import Drone

class orchestrator(flychestrator):

    def plan(drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]]
        ) -> dict[int, list[MovementRecord]]:

        while all nodes are .deivered:
            for drone in drones:
                for index, (total_cost, route) in routes.items():
                    if drone.current_route == 0: #primera ruta:

                        #De esta manera identificamos el siguiente nodo
                        index = pos_next_node(drone.current_node, route)
                        next_node = route[index]

                        if next_node.available_node():

                            #avanzamos el drone.
                            drone.move_to_node(next_node)
                            next_node.exit_drone(drone)

                        else:

    def pos_next_node(current_node: Node, route: tuple[Node, ...]) -> int:
        for index, node in enumerate(route):
            if node == current_node:
                return index + 1
        return None
                
