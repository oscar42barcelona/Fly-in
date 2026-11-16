from abc import ABC, abstractmethod
from ..Graph.Drone import Drone
from ..Graph.Map import Graph, Node


class flygorithm(ABC):

    @abstractmethod
    def solve(
        self,
        drone: Drone,
        graph: Graph,
        k: int = 3
        ) -> list[tuple[int, tuple[Node, ...]]]:
        pass
