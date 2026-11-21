from dataclasses import dataclass

from DroneGen.Graph.Drone import Drone
from DroneGen.Graph.Map import Node, Connection


@dataclass(frozen=True)
class MovementIntent:
    drone: Drone
    origin: Node | None
    destination: Node
    connection: Connection
