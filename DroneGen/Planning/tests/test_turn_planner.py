
import unittest
from typing import cast
from DroneGen.base import State
from input.validator import HubType, Zone
from DroneGen.Graph.Map import Node, Connection, Graph
from DroneGen.Graph.Drone import Drone
from DroneGen.Planning.TurnPlanner import TurnPlanner


class TestTurnPlanner(unittest.TestCase):

    def test_collect_intents_does_not_move_drone(self) -> None:

        # 1. Crear un grafo A ---- B
        node_a = Node(
            "A", 0, 0,
            cast(HubType, "entry"),
            cast(Zone, "normal"),
            "green", 1
        )

        node_b = Node(
            "B", 1, 0,
            cast(HubType, "exit"),
            cast(Zone, "normal"),
            "yellow", 1
        )

        edge = Connection(node_a, node_b, 1)
        graph = Graph([node_a, node_b], [edge])

        # 2. Crear un dron en A
        drone = Drone(1, node_a)
        node_a.enter_drone(drone)

        # 3. Asignar una ruta
        routes = {
            0: (1, (node_a, node_b))
        }

        # 4. Recoger propuestas
        planner = TurnPlanner()

        intents = planner.collect_intents(
            [drone], routes, graph
        )

        # 5. Comprobar la propuesta
        self.assertEqual(len(intents), 1)

        intent = intents[0]

        self.assertIs(intent.drone, drone)
        self.assertIs(intent.origin, node_a)
        self.assertIs(intent.destination, node_b)
        self.assertIs(intent.connection, edge)

        # 6. Comprobar que nada se ha movido
        self.assertIs(drone.current_node, node_a)
        self.assertIn(drone, node_a.drones)
        self.assertNotIn(drone, node_b.drones)
        self.assertEqual(edge.drones, [])

    def test_delivered_drone_has_no_intent(self) -> None:

        node_a = Node(
            "A", 0, 0,
            HubType.ENTRY,
            Zone.NORMAL,
            "green", 1
        )

        node_b = Node(
            "B", 1, 0,
            HubType.EXIT,
            Zone.NORMAL,
            "yellow", 1
        )

        edge = Connection(node_a, node_b, 1)
        graph = Graph([node_a, node_b], [edge])

        drone = Drone(1, node_b)
        drone.delivered = True

        routes = {
            0: (1, (node_a, node_b))
        }

        planner = TurnPlanner()
        intents = planner.collect_intents([drone], routes, graph)

        self.assertEqual(len(intents), 0)
        self.assertTrue(drone.delivered)
        self.assertIs(drone.current_node, node_b)

    def test_drone_in_transit_has_arrival_intent(self) -> None:
        node_a = Node(
            "A", 0, 0,
            HubType.ENTRY,
            Zone.NORMAL,
            "green", 1
        )

        node_b = Node(
            "B", 1, 0,
            HubType.INTERMEDIATE,
            Zone.RESTRICTED,
            "red", 1
        )

        edge = Connection(node_a, node_b, 1)
        graph = Graph([node_a, node_b], [edge])

        drone = Drone(1, node_a)
        drone.start_restricted_transit(edge, node_b)
        edge.enter_connection(drone)

        routes = {
            0: (2, (node_a, node_b))
        }

        planner = TurnPlanner()
        intents = planner.collect_intents([drone], routes, graph)

        self.assertEqual(len(intents), 1)

        intent = intents[0]

        self.assertIs(intent.drone, drone)
        self.assertIsNone(intent.origin)
        self.assertIs(intent.destination, node_b)
        self.assertIs(intent.connection, edge)

        # Todavía no hemos ejecutado el movimiento.
        self.assertEqual(drone.state, State.TRANSIT)
        self.assertIsNone(drone.current_node)
        self.assertIn(drone, edge.drones)
