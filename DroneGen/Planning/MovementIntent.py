from dataclasses import dataclass
from enum import Enum, auto

from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Node, Connection


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
