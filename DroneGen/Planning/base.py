from abc import ABC, abstractmethod

from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Node, Graph
from DroneGen.Planning.MovementIntent import MovementIntent


class BaseTurnPlanner(ABC):

    @abstractmethod
    def collect_intents(
        self,
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        graph: Graph
    ) -> list[MovementIntent]:
        pass
