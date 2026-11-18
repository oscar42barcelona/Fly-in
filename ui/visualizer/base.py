from DroneGen.base import MovementRecord
from DroneGen.Graph.Map import Node, Connection, Graph
from abc import ABC, abstractmethod


class Visualizer(ABC):

    def __init__(
        self,
        graph: Graph,
    ) -> None:
        #self.node = node
        #self.connection = connection
        self.graph = graph

    @abstractmethod
    def create_visualization(self, 
        turn_movements: dict[int, list[MovementRecord]]) -> None:
        pass
