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

        #heap = []
        next_node: Node #este sera el proximo node al que se ira

        connection_list: list[Node] = graph.get_connections(drone.current_node)
        """vale pero yo quiero ahora calcular el camino menos pesado de todos los caminosposible"""

        #heappush(heap, )
        node in connection_list:
        """Con este bucle estamos viendo cual es nodo siguiente al que vamos"""
            if node.cost is not None:
                heappush(heap, (node.cost, node.priority, node.name, node))
            """cosas por cerrar
                que pasa con none es decir si todos son blocked"""

        next_node = heappop(heap)
        drone.move_to_node(next_node)
        if next_node.enter_drone(drone) is False:
            """habria que ir a otro nodo no?"""
        """hoy hemos empezado a ver como avanzamos los nodos
            a ver que bola"""

