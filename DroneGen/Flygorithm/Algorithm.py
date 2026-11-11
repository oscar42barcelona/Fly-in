from input.validator import Zone
from .base import MovementRecord, flygorithm
from Flygorithm.Drone import Drone
from Flygorithm.Map import Node, Connection, Graph
from heapq import heappush, heappop, heapify

class Algorithm(flygorithm):
    def solve(self, drones: list[Drone], graph: Graph) -> dict[int, list[MovementRecord]]:
        ...


    def first_drone_djikstra(self, drone: Drone, 
            graph: Graph) -> dict[int, list[MovementRecord]]:

        heap = []

        next_node: Node #este sera el proximo node al que se ira
        visited_nodes: list[Node] = [] #?

        connection_list: list[Node] = graph.get_connections(drone.current_node)

        node in connection_list:
        """Con este bucle estamos viendo cual es nodo siguiente al que vamos"""
            if node.zone.cost is not None:
                heappush(heap, (node.zone.cost, node.zone.priority, node.name, node))
            """cosas por cerrar
                que pasa con none es decir si todos son blocked"""

        c, p, n, next_node = heappop(heap)
        drone.move_to_node(next_node)
        if next_node.enter_drone(drone) is False:
            """habria que ir a otro nodo no"""

    def djikstra_route_finding(self, drone: Drone,
            graph: Graph) -> dict[int, list[MovementRecord]]:

        heap = []
        node_list: list[Node]

        cumulative_cost: int

        next_node = drone.current_node

        node_list.append(next_node)

        while next_node != "goal":

            connection_list = [node for node in graph.get_connections(next_node) if node not in node_list]

            for node in connection_list:

                if node.zone.cost is not None:

                    if next_node.name == "start"
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

        
    def comprob_menor_coste(self, heap, node, cumulative_cost) -> (bool, int):

        for index, tupla in enumerate(heap):
            if node in tupla[3]:

                 if tupla[0] < cumulative_cost:
                    return (True, 0)

                elif tupla[0] >= cumulative_cost:
                    return (True, index)
            else:
                return (False, 0)
                
        


            """Esto en teoria es hasta encontrar la primera ruta
            Aqui tenemos que guardar el coste y hacer otro bucle a ver 
            si podemos optimizar las rutas y 
            me interesa en realidad guarda todas las rutas
            Como guardo las rutas?
            Como reconstruyo las rutas?"""
