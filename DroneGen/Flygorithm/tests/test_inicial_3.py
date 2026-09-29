from __future__ import annotations
from collections.abc import Generator
from collections import deque

class Node:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        entry: bool = False,
        exit: bool = False,
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.entry = entry
        self.exit = exit
        self.connections: list[Node] = []
        self.nb_drones: int = 0

    def connect(self, node: Node) -> None:
        self.connections.append(node)
        node.connections.append(self)

    def __repr__(self) -> str:
        return self.name


a = Node("a", 3, 5, entry=True)
b = Node("b", 7, 9)
c = Node("c", 7, 1)
d = Node("d", 11, 5)
e = Node("e", 15, 5, exit=True)

f = Node("f", 9, 12)
g = Node("g", 12, 12)

a.connect(b)
a.connect(c)
b.connect(f)
b.connect(d)
c.connect(d)
d.connect(e)

nodes = [a, b, c, d, e, f, g]

class Drone():
    def __init__(self, drone_number: int, starting_node: node) -> None:
        self.number = drone_number
        self.starting_node = starting_node
        self.current_node: node = starting_node

    def current_stop(self, current_node: node) -> None:
        self.current_node = current_node
        current_node.nb_drones += 1
        """if previous_node.nb_drones > 0:
            previous_node.nb_drones -= 1"""

d1 = Drone(1, a)
d2 = Drone(2, a)

def FourthAlgorithm(drone: Drone) -> Generator[tuple[int, int], None, None]:
    available_nodes: list[node] = []
    visited_nodes: list[node] = []

    visited_nodes.append(drone.starting_node)
    yield (drone)

    goback:int = 2
    while (drone.current_node.exit is False):
        available_nodes = [node for node in drone.current_node.connections if node not in visited_nodes]
        if not available_nodes:
            path : list[node] = visited_nodes.copy()
            drone.current_stop(path[-goback])
            yield (drone)
            goback += 1
            continue
        av_node = deque(available_nodes)
        new_node: node = av_node.popleft()
        drone.current_stop(new_node)
        visited_nodes.append(new_node)
        yield (drone)
        goback = 2
    print("Se acabó lo que se daba")


def main() -> None:
    trip_1 = FourthAlgorithm(d1)
    trip_2 = FourthAlgorithm(d2)
    

    while True:
        input("Press Enter to move the drone...")

        try:
            drone_1 = next(trip_1)
            drone_2 = next(trip_2)
            
            print(
                f"Drone {drone_1.number} is at node {drone_1.current_node.name} in positions: "
                f"({drone_1.current_node.x}, {drone_1.current_node.y})"
            )

            print(
                f"Drone {drone_2.number} is at node {drone_2.current_node.name} in positions: "
                f"({drone_2.current_node.x}, {drone_2.current_node.y})"
            )

        except StopIteration:
            print("The drone has reached the exit")
            break


if __name__ == "__main__":
    main()
