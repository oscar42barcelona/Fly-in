from input.validator import Zone
from .base import MovementRecord, flygorithm
from ..Graph.Drone import Drone
from ..Graph.Map import Node, Connection, Graph
from heapq import heappush, heappop, heapify

class Algorithm(flygorithm):
    def solve(self, drone: Drone, graph: Graph) -> dict[int, list[MovementRecord]]:
        ...

    def djikstra_route_finding(self, drone: Drone,
            graph: Graph) -> list[Node]:

        heap = []

        node_list: list[Node] = []

        cumulative_cost: int = 0

        next_node = drone.current_node

        node_list.append(next_node)

        while next_node.name != "goal":

            connection_list = [node for node in graph.get_connections(next_node) if node not in node_list]

            for node in connection_list:

                if node.zone.cost is not None:

                    if next_node.name == "start":
                        cumulative_cost = node.zone.cost
                    else:
                        cumulative_cost = node.zone.cost + cumulative_cost

                    comprob = self.comprob_menor_coste(heap, node, cumulative_cost)

                    if comprob[0]:
                        if not comprob[1]:
                            continue
                        heap.remove[comprob[1]]
                         
                    heappush(heap, (cumulative_cost, node.zone.priority, node.name, node, node_list))

                cumulative_cost, _, _, next_node, node_list = heappop(heap)

                node_list.append(next_node)

        return node_list

        
    def comprob_menor_coste(self, heap, node, cumulative_cost) -> (bool, int):

        for index, tupla in enumerate(heap):
            if node in tupla[3]:

                if tupla[0] < cumulative_cost:
                    return (True, 0)

                elif tupla[0] >= cumulative_cost:
                    return (True, index)
            else:
                return (False, 0)
                


