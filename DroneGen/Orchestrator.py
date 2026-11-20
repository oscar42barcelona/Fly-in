from .base import flychestrator, MovementRecord, State
from input.validator import Zone #, HubType
from DroneGen.Graph.Map import Node, Graph, Connection
from DroneGen.Graph.Drone import Drone
#from heapq import heappush, heappop, heapify


class orchestrator(flychestrator):

    def plan(self, drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
         graph: Graph
        ) -> dict[int, list[MovementRecord]]:

        movement_record: list[MovementRecord]
        turn_movement_record = {}
        turn = 0

        while any(not drone.delivered for drone in drones):

            movement_record = []
            
            for drone in drones:

                if drone.delivered is True:
                    continue

                if drone.state != State.TRANSIT:
                    
                    #De esta manera identificamos el siguiente nodo
                    route_cost, route = routes[drone.current_route]
                    index = self.pos_next_node(drone.current_node, route)
                    if index is None:
                        continue
                    next_node = route[index]

                    #Si no puedo entrar el nodo...
                    if next_node.available_node() is False:
                        next_node = self.search_enter(routes,
                                        drone, next_node, graph
                                                )
                    #Si es None hay que esperar en el mismo drone
                    if next_node is None:
                        route[index].queueing_drones_ft(drone)
                        drone.move_to_node(drone.current_node) #No?
                    else:
                        edge = self.search_connection(drone.current_node, next_node, graph)
                        #si es None es que no se ha encontrado conexion (resolver...)
                        if edge is not None and edge.available_connection():

                            drone.current_node.exit_drone(drone)
                            edge.enter_connection(drone)

                            if next_node.zone == Zone.RESTRICTED:
                                next_node.reserved_drones.append(drone)
                                drone.start_restricted_transit(edge, next_node)

                            else:
                                next_node.enter_drone(drone)
                                drone.move_to_node(next_node)
                                edge.exit_connection(drone)
                else:
                    next_node = drone.headed_to

                    drone.current_connection.exit_connection(drone)

                    drone.move_to_node(next_node)
                    drone.end_restricted_transit()
                    next_node.enter_drone(drone)

                if drone.state == State.TRANSIT:
                    edge = drone.current_connection
                    location = f"{edge.node_a.name}-{edge.node_b.name}"
                else:
                    location = drone.current_node.name

                #registramos el movement_record
                movement_record.append(MovementRecord(
                    drone.id,
                    drone.state,
                    drone.current_node.name)) #voy a arreglar esto porque arriba hago exit

            turn += 1
    
            turn_movement_record[turn] = movement_record
        
        return turn_movement_record

    def search_enter(
        self,
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        drone: Drone,
        previous_node: Node,
        graph: Graph
        ) -> Node | None:

        initial_route = drone.current_route

        for route_index, (route_cost, route) in routes.items():

            if route_index == initial_route:
                continue

            #De esta manera identificamos el siguiente nodo
            index = self.pos_next_node(drone.current_node, route)
            if index is None:
                continue
            next_node = route[index]

            edge = self.search_connection(drone.current_node,
                                    next_node, graph)

            if edge is None:
                continue

            if not next_node.available_node():
                continue

            if not edge.available_connection():
                continue

            _, previous_route = routes[drone.current_route]

            previous_path_cost = self.path_cost(drone.current_node,
                                    previous_route)

            current_path_cost = self.path_cost(drone.current_node,
                                route)

            waiting_cost = len(previous_node.queueing_drones)

            previous_total_cost = previous_path_cost + waiting_cost

            if previous_total_cost > current_path_cost:

                if drone in previous_node.queueing_drones:
                    previous_node.queueing_drones.remove(drone)

                drone.current_route = route_index
                return next_node

        return None


    def pos_next_node(self,
            current_node: Node,
            route: tuple[Node, ...]) -> int | None:
        """devolvemos el indice del nodo siguiente que toca en el mapa"""
        for index, node in enumerate(route):
            if node == current_node:
                if index + 1 < len(route):
                    return index + 1
        return None

    def path_cost(self,
            current_node: Node,
            route: tuple[Node, ...]) -> int | None:
        """coste desde el nodo actual hasta el final"""
        index = self.pos_next_node(current_node, route)

        if index is None:
            return 0

        path_cost: int = 0

        for node in route[index:]: #revisar si se acaba en el end_hub

            path_cost = path_cost + node.zone.cost

        return path_cost

    def search_connection(self, previous_node: Node, 
                        next_node: Node,
                        graph: Graph
                        ) -> Connection:

        edge = next(
            (
                edge for edge in graph.connections
                if (edge.node_a == previous_node and
                    edge.node_b == next_node)
                or
                (edge.node_b == previous_node and
                edge.node_a == next_node)
            ),
            None
            )
        
        return edge
        
        
