from input.validator import Zone
from .base import MovementRecord, flygorithm
from ..Graph.Drone import Drone
from ..Graph.Map import Node, Connection, Graph
from heapq import heappush, heappop, heapify
from itertools import count


class Algorithm(flygorithm):
    def solve(self, drone: Drone, graph: Graph) -> dict[int, list[MovementRecord]]:
        ...

    
    def djikstra_route_finding(self, drone: Drone, graph: Graph):

        heap = []
        contador = count()
        goal_routes = []

        next_node = drone.current_node
        tuple_list = (next_node,)

        heappush(heap, (
            0,
            next_node.zone.priority,
            next(contador),
            next_node,
            tuple_list
        ))

        while heap:

            previous_cost, _, _, next_node, tuple_list = heappop(heap)

            if next_node.name == "goal":
                goal_routes.append((previous_cost, tuple_list))
                continue

            connection_list = [
                node
                for node in graph.get_connections(next_node)
                if node not in tuple_list
                ]

            for node in connection_list:

                if node.zone.cost is not None:

                    cumulative_cost = previous_cost + node.zone.cost

                    heappush(heap, (
                        cumulative_cost,
                        node.zone.priority,
                        next(contador),
                        node,
                        tuple_list + (node,)
                    ))

        return goal_routes

        
    def comprob_menor_coste(self, heap, node, cumulative_cost) -> tuple[bool, int | None]:

        if not heap:
            return (False, 0)
        for index, tupla in enumerate(heap):
            if node == tupla[3]:

                if tupla[0] < cumulative_cost:
                    return (True, None)

                else:
                    return (True, index)

        return (False, 0)

    
    def original_djikstra_route_finding(self, drone: Drone,
            graph: Graph) -> list[Node]:

        heap = []

        node_list: list[Node] = []

        cumulative_cost: int = 0

        next_node = drone.current_node

        tuple_list = (next_node,)

        while next_node.name != "goal":

            connection_list = [node for node in graph.get_connections(next_node) if node not in tuple_list]

            for node in connection_list:

                if node.zone.cost is not None:

                    if next_node.type == "entry":
                        cumulative_cost = node.zone.cost
                    else:
                        cumulative_cost = node.zone.cost + previous_cost

                    flag, index = self.comprob_menor_coste(heap, node, cumulative_cost)

                    if flag:
                        if not index:
                            continue
                        heap.pop(index)

                        heapify(heap)

                    heappush(heap, (cumulative_cost, node.zone.priority, node.name, node, tuple_list))

            previous_cost, _, _, next_node, previous_tuple = heappop(heap)

            tuple_list = (previous_tuple + (next_node,))


        return tuple_list
