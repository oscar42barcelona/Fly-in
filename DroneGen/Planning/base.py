"""Movement intent types and the abstract turn planner interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Connection, Graph, Node


class MovementKind(Enum):
    """The three transitions supported by the turn scheduler."""

    NORMAL = auto()
    START_TRANSIT = auto()
    END_TRANSIT = auto()


@dataclass(frozen=True)
class MovementIntent:
    """A proposed movement that has not yet been approved."""

    drone: Drone
    origin: Node | None
    destination: Node
    connection: Connection
    kind: MovementKind


class BaseTurnPlanner(ABC):
    """Define how planners collect movement intents."""

    @abstractmethod
    def collect_intents(
        self,
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        graph: Graph,
    ) -> list[MovementIntent]:
        """Propose the next movement for each active drone."""
        raise NotImplementedError
