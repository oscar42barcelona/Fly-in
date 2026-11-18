from .base import flychestrator, MovementRecord
from input.validator import Zone #, HubType
from Graph.Map import Node, Connection
from Graph.Drone import Drone
from heapq import heappush, heappop, heapify


class orchestrator(flychestrator):

    def plan(drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]]
        ) -> dict[int, list[MovementRecord]]:

        movement_record: list[MovementRecord] = []

        delivered_count = 0

        len_drones = len(drones)

        while delivered_count < len_drones:

            for drone in drones if drone.delivered is False:
                
                #De esta manera identificamos el siguiente nodo
                route_cost, route = routes[self.current_route]
                index = pos_next_node(drone.current_node, route)
                next_node = route[index]

                #Si no puedo entrar el nodo...
                if next_node.available_node() is False:
                    next_node = search_enter(routes, drone, next_node)

                if next_node is None:
                    queueing_drones(drone)
                else:
                    drone.current_node.exit_drone(drone)
                    next_node.enter_drone(drone)

                drone.move_to_node(next_node) #si decidimos no avanzar, next_node debe de ser el mismo nodo

                #registramos el movement_record
                #movement = "movement_" + "" + Como cuento los turnos???
                movement_record.append(MovementRecord(
                    drone.id,
                    drone.state,
                    current_node))

                if drone.delivered is True:
                    delivered_count += 1

    def search_enter(
        routes: dict[int, list[MovementRecord]],
        drone: Drone,
        previous_node: Node,
        ) -> Node:

        initial_route = drone.current_route

        graph = graph()

        for route_index, (route_cost, route) in routes.items():

            if route_index == initial_route:
                continue

            #De esta manera identificamos el siguiente nodo
            index = pos_next_node(drone.current_node, route)
            next_node = route[index]

            connection_list = graph.get_connections(node)

            #Si no se puede pasar o no se puede llegar porque no esta conectado
            if next_node.available_node() is False
                and drone.current_node not in connection_list:
                continue

            previous_path_cost = path_cost(previous_node, route)

            current_path_cost = path_cost(next_node, route)

            waiting_cost = len(previous_node.queueing_drones)

            previous_total_cost = previous_path_cost + waiting_cost

            if previous_total_cost > current_path_cost:
                drone.current_route = route_index
                return next_node
            else:
                return None


    def pos_next_node(current_node: Node, route: tuple[Node, ...]) -> int:
        """devolvemos el indice del nodo siguiente que toca en el mapa"""
        for index, node in enumerate(route):
            if node == current_node:
                return index + 1
        return None

    def path_cost(current_node: Node, route: tuple[Node, ...]) -> int
        """coste desde el nodo actual hasta el final"""
        index = pos_next_node(current_node, route)

        path_cost: int = 0

        for node in route[index:-1]: #revisar si se acaba en el end_hub

            path_cost = path_cost + node.zone.cost
