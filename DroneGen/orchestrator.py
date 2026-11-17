from .base import flychestrator, MovementRecord
from input.validator import Zone #, HubType
from Graph.Map import Node, Connection
from Graph.Drone import Drone

class orchestrator(flychestrator):

    def plan(drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]]
        ) -> dict[int, list[MovementRecord]]:

        movement_record: list[MovementRecord] = []

        while all nodes are .deivered:
            for drone in drones:
                for _, (route_cost, route) in routes.items():

                    #De esta manera identificamos el siguiente nodo
                    index = pos_next_node(drone.current_node, route)
                    next_node = route[index]

                    if drone.current_route == 0: #primera ruta:

                        if next_node.available_node():

                            #avanzamos el drone.
                            drone.current_node.exit_drone(drone)
                            drone.move_to_node(next_node)
                            next_node.enter_drone(drone)

                            #registramos el movement_record
                            #movement = "movement_" + "" + Como cuento los turnos?
                            movement_record.append(MovementRecord(
                                drone.id,
                                drone.state,
                                current_node))
                            break
                    else:
                        
                        if next_node.available_node():
                            tota_cost = path_cost(drone.current_node, route)
                            if total_cost + 

                            
                             

                            

    def pos_next_node(current_node: Node, route: tuple[Node, ...]) -> int:
        for index, node in enumerate(route):
            if node == current_node:
                return index + 1
        return None

    def path_cost(current_node: Node, route: tuple[Node, ...]) -> int
        index = pos_next_node(current_node, route)

        path_cost: int = 0

        for node in route[index:-1]: #revisar si se acaba en el end_hub

            path_cost = path_cost + node.zone.cost

        return path_cost
            
                
