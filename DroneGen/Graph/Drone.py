"""Drone state transitions between nodes and restricted connections."""

from __future__ import annotations

from typing import TYPE_CHECKING

from DroneGen.base import State
from input.validator import HubType

if TYPE_CHECKING:
    from .Map import Connection, Node


class Drone:
    """A single drone with its current location and route assignment."""

    def __init__(self, id_: int, start_node: Node) -> None:
        """Place the drone at the entry node before simulation starts."""
        self.id = id_
        self.current_node: Node | None = start_node
        self.current_connection: Connection | None = None
        self.headed_to: Node | None = None
        self.delivered = False
        self.state = State.STAY
        self.current_route = 0

    def move_to_node(self, destination: Node) -> None:
        """Move directly to a normal/priority node in one turn."""
        if destination == self.current_node:
            self.state = State.STAY
            return

        if destination.type == HubType.EXIT:
            self.delivered = True

        self.current_node = destination
        self.state = State.MOVEMENT

    def start_restricted_transit(
        self, connection: Connection, destination: Node
    ) -> None:
        """Occupy the link before entering a restricted node."""
        self.current_connection = connection
        self.current_node = None
        self.state = State.TRANSIT
        self.headed_to = destination

    def end_restricted_transit(self) -> None:
        """Complete the mandatory second turn of a restricted crossing."""
        self.current_connection = None
        self.current_node = self.headed_to
        self.headed_to = None
        self.state = State.MOVEMENT
