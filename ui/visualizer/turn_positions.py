"""Reconstruct per-turn drone positions without mutating simulation state."""

from __future__ import annotations

from DroneGen.base import MovementRecord, State
from DroneGen.Graph.Map import Connection, Graph, Node
from input.validator import HubType, Zone

DronePosition = Node | Connection
TurnPositions = dict[int, dict[int, DronePosition]]


class TurnPositionReplayer:
    """Resolve each drone's location from the ordered movement history."""

    def __init__(self, graph: Graph) -> None:
        """Store map geometry for looking up nodes and connections."""
        self.graph = graph

    def replay(
        self,
        turn_movements: dict[int, list[MovementRecord]],
    ) -> TurnPositions:
        """Return positions for turn zero and every completed turn."""
        starts = [
            node for node in self.graph.nodes
            if node.type == HubType.ENTRY
        ]
        if len(starts) != 1:
            raise ValueError("Expected exactly one entry node")

        start = starts[0]
        nodes: dict[str, Node] = {
            node.name: node for node in self.graph.nodes
        }
        connections: dict[str, Connection] = {}
        for connection in self.graph.connections:
            a, b = connection.node_a, connection.node_b
            connections[f"{a.name}-{b.name}"] = connection
            connections[f"{b.name}-{a.name}"] = connection

        drone_ids = sorted({
            record.drone_id
            for records in turn_movements.values()
            for record in records
        })
        current: dict[int, DronePosition] = {
            drone_id: start for drone_id in drone_ids
        }
        snapshots: TurnPositions = {0: current.copy()}
        pending: dict[int, Node] = {}

        for turn in range(1, max(turn_movements, default=0) + 1):
            seen: set[int] = set()
            arriving: set[int] = set()
            new_pending: dict[int, Node] = {}

            for record in turn_movements.get(turn, []):
                drone_id = record.drone_id
                if drone_id in seen:
                    raise ValueError(
                        f"D{drone_id}: duplicate record in turn {turn}"
                    )
                seen.add(drone_id)
                previous = current[drone_id]

                if drone_id in pending:
                    expected = pending[drone_id]
                    if (
                        record.state != State.MOVEMENT
                        or record.location != expected.name
                    ):
                        raise ValueError(
                            f"D{drone_id}: expected arrival at "
                            f"{expected.name}"
                        )
                    arriving.add(drone_id)

                if record.state == State.TRANSIT:
                    transit_connection = connections.get(record.location)
                    if transit_connection is None or not isinstance(previous, Node):
                        raise ValueError(
                            f"D{drone_id}: invalid restricted transit"
                        )
                    if previous is transit_connection.node_a:
                        destination = transit_connection.node_b
                    elif previous is transit_connection.node_b:
                        destination = transit_connection.node_a
                    else:
                        raise ValueError(
                            f"D{drone_id}: transit from wrong node"
                        )
                    if destination.zone != Zone.RESTRICTED:
                        raise ValueError(
                            f"D{drone_id}: transit target is not restricted"
                        )
                    current[drone_id] = transit_connection
                    new_pending[drone_id] = destination

                elif record.state == State.MOVEMENT:
                    target_node = nodes.get(record.location)
                    if target_node is None:
                        raise ValueError(
                            f"D{drone_id}: unknown destination"
                        )
                    if isinstance(previous, Connection):
                        if target_node not in (
                            previous.node_a, previous.node_b
                        ):
                            raise ValueError(
                                f"D{drone_id}: arrival is not on link"
                            )
                    elif previous is not target_node and not any(
                        (edge.node_a is previous
                         and edge.node_b is target_node)
                        or (edge.node_b is previous
                            and edge.node_a is target_node)
                        for edge in self.graph.connections
                    ):
                        raise ValueError(
                            f"D{drone_id}: nonadjacent movement"
                        )
                    current[drone_id] = target_node

                elif record.state == State.STAY:
                    if (
                        not isinstance(previous, Node)
                        or record.location != previous.name
                    ):
                        raise ValueError(
                            f"D{drone_id}: invalid stay"
                        )

                else:
                    raise ValueError(
                        f"D{drone_id}: unknown movement state"
                    )

            if arriving != set(pending):
                raise ValueError(
                    f"Turn {turn}: missing mandatory restricted arrival"
                )
            pending = new_pending
            snapshots[turn] = current.copy()

        if pending:
            raise ValueError("Simulation ended during a restricted transit")
        return snapshots
