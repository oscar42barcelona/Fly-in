"""Abstract interface for the multi-route pathfinding algorithm."""

from abc import ABC, abstractmethod

from ..Graph.Drone import Drone
from ..Graph.Map import Graph, Node


class flygorithm(ABC):
    """Define a route solver returning costs and node sequences."""

    @abstractmethod
    def solve(
        self,
        drone: Drone,
        graph: Graph,
        k: int = 3,
    ) -> dict[int, tuple[int, tuple[Node, ...]]]:
        """Return at most k alternative routes indexed by route identifier."""
        raise NotImplementedError
