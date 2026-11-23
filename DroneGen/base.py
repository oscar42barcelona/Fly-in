"""Abstract simulation orchestrator and immutable movement records."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Graph.Drone import Drone
    from .Graph.Map import Graph, Node


class State(Enum):
    """A drone's state after its approved movement in one turn."""

    MOVEMENT = "movement"
    TRANSIT = "transit"
    STAY = "stay"


@dataclass(frozen=True)
class MovementRecord:
    """The identity, state and location of one drone after a turn."""

    drone_id: int
    state: State
    location: str


class flychestrator(ABC):
    """Define the interface for coordinating drone moves by turn."""

    @abstractmethod
    def plan(
        self,
        drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]],
        graph: Graph,
    ) -> dict[int, list[MovementRecord]]:
        """Return a chronological record of each turn's movements."""
        raise NotImplementedError
