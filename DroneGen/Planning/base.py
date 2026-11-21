from abc import ABC, abstractmethod
from dataclasses import dataclass
from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Node, Graph, Connection

class MovementKind(Enum):
    NORMAL = auto()
    START_TRANSIT = auto()
    END_TRANSIT = auto()


@dataclass(frozen=True)
class MovementIntent:
    drone: Drone
    origin: Node | None
    destination: Node
    connection: Connection
    kind: MovementKind

class BaseTurnPlanner(ABC):

    @abstractmethod
    def collect_intents(
        self,
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        graph: Graph,
    ) -> list[MovementIntent]:
        pass
