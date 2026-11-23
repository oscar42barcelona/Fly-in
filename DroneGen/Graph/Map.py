"""Graph objects and capacity bookkeeping for Fly-in."""

from __future__ import annotations

from input.validator import HubType, Zone

from .Drone import Drone


class Node:
    """A named map zone with limited space for drones."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        hub_type: HubType,
        zone: Zone,
        color: str,
        max_drones: int,
    ) -> None:
        """Store hub metadata and initialize its drone collections."""
        self.name = name
        self.x = x
        self.y = y
        self.type = hub_type
        self.zone = zone
        self.COLOR = color
        self.capacity = max_drones
        self.drones: list[Drone] = []
        self.queueing_drones: list[Drone] = []
        self.reserved_drones: list[Drone] = []

    def available_node(self) -> bool:
        """Check whether the node can accommodate another drone."""
        if self.type in (HubType.ENTRY, HubType.EXIT):
            return True
        if len(self.drones) >= self.capacity:
            return False
        occupied = len(self.drones) + len(self.reserved_drones)
        return occupied < self.capacity

    def queueing_drones_ft(self, drone: Drone) -> list[Drone]:
        """Register a waiting drone and expose the current queue."""
        if drone not in self.queueing_drones:
            self.queueing_drones.append(drone)
        return self.queueing_drones

    def enter_drone(self, drone: Drone) -> bool:
        """Occupy a node, respecting existing reservations and capacity."""
        if drone not in self.reserved_drones:
            if not self.available_node():
                return False
        else:
            self.reserved_drones.remove(drone)

        if drone in self.queueing_drones:
            self.queueing_drones.remove(drone)

        self.drones.append(drone)
        return True

    def exit_drone(self, drone: Drone) -> bool:
        """Remove a drone from this node."""
        self.drones.remove(drone)
        return True


class Connection:
    """A bidirectional link with a capacity limit for transiting drones."""

    def __init__(
        self,
        node_a: Node,
        node_b: Node,
        max_link_capacity: int,
    ) -> None:
        """Connect two nodes and initialize the link occupancy."""
        self.node_a = node_a
        self.node_b = node_b
        self.capacity = max_link_capacity
        self.drones: list[Drone] = []

    def available_connection(self) -> bool:
        """Check whether another drone may occupy this connection."""
        return len(self.drones) < self.capacity

    def enter_connection(self, drone: Drone) -> bool:
        """Add a drone to the link when a place is available."""
        if not self.available_connection():
            return False
        self.drones.append(drone)
        return True

    def exit_connection(self, drone: Drone) -> bool:
        """Remove a drone after a completed crossing."""
        self.drones.remove(drone)
        return True

    def get_midpoint(self) -> tuple[float, float]:
        """Return the coordinates halfway between the two endpoints."""
        return (
            (self.node_a.x + self.node_b.x) / 2,
            (self.node_a.y + self.node_b.y) / 2,
        )


class Graph:
    """Hold all map zones and their undirected connections."""

    def __init__(
        self,
        nodes: list[Node],
        connections: list[Connection],
    ) -> None:
        """Store the graph's nodes and links."""
        self.nodes = nodes
        self.connections = connections

    def get_connections(self, node: Node) -> list[Node]:
        """Return every directly connected neighboring node."""
        neighbors: list[Node] = []
        for connection in self.connections:
            if node is connection.node_a:
                neighbors.append(connection.node_b)
            elif node is connection.node_b:
                neighbors.append(connection.node_a)
        return neighbors
