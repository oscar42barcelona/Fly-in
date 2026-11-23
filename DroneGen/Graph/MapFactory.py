"""Construct typed graph and drone objects from validated input models."""

from __future__ import annotations

from input.validator import Connection as ValidatedConnection
from input.validator import Hub

from .Drone import Drone
from .Map import Connection, Graph, Node


class Factory:
    """Create simulation objects from Pydantic map descriptions."""

    def __init__(self) -> None:
        """Initialize per-simulation drone identifiers."""
        self.drone_id = 0

    def create_drone(self, start_node: Node) -> Drone:
        """Create the next drone with a unique identifier."""
        self.drone_id += 1
        return Drone(self.drone_id, start_node)

    def create_drones(self, nb_drones: int, start_node: Node) -> list[Drone]:
        """Create all drones and register them in the entry node."""
        drones: list[Drone] = []
        for _ in range(nb_drones):
            drone = self.create_drone(start_node)
            start_node.enter_drone(drone)
            drones.append(drone)
        return drones

    def create_node(self, hub: Hub) -> Node:
        """Create one graph node from its validated definition."""
        return Node(
            name=hub.NAME,
            x=hub.X,
            y=hub.Y,
            hub_type=hub.TYPE,
            zone=hub.ZONE,
            color=hub.COLOR or "grey",
            max_drones=hub.MAX_DRONES,
        )

    def create_nodes(self, node_list: list[Hub]) -> list[Node]:
        """Create the full collection of nodes."""
        return [self.create_node(hub) for hub in node_list]

    def create_connection(
        self,
        connection: ValidatedConnection,
        node_list: list[Node],
    ) -> Connection:
        """Connect the two nodes named in a validated link."""
        nodes = {node.name: node for node in node_list}
        capacity = connection.LINK_CAPACITY
        return Connection(
            node_a=nodes[connection.HUB1],
            node_b=nodes[connection.HUB2],
            max_link_capacity=capacity if capacity is not None else 1,
        )

    def create_connections(
        self,
        connect_list: list[ValidatedConnection],
        node_list: list[Node],
    ) -> list[Connection]:
        """Create every connection in the map."""
        return [
            self.create_connection(connection, node_list)
            for connection in connect_list
        ]

    def create_graph(
        self,
        hubs: list[Hub],
        connections: list[ValidatedConnection],
    ) -> Graph:
        """Return a graph from all validated zones and links."""
        nodes = self.create_nodes(hubs)
        links = self.create_connections(connections, nodes)
        return Graph(nodes, links)
