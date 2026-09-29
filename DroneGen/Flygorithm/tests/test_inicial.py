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


f.connect(g)

nodes = [a, b, c, d, e, f, g]

class Drone():
    def __init__(self, drone_number: int, starting_node: node) -> None:
        self.drone_number = drone_number
        self.starting_node = starting_node
        self.current_node: node

    def current_stop(self, previous_node: node, current_node: node) -> None:
        self.current_node = current_node
        current_node.nb_drones += 1
        if previous_node.nb_drones > 0:
            previous_node.nb_drones -= 1 


def drone(node: node):
    print(f"Drone is at {node.name}")


def FirstAlgorithm():
    available_nodes: list[node] = []
    visited_nodes: list[node] = []
    
    new_node: node = a
    visited_nodes.append(a)
    drone(new_node)

    goback:int = 2
    while (new_node.exit is False):
        available_nodes = [node for node in new_node.connections if node not in visited_nodes]
        if not available_nodes:
            path : list[node] = visited_nodes.copy()
            new_node = path[-goback]
            drone(new_node)
            goback += 1
            continue
        av_node = deque(available_nodes)
        new_node = av_node.popleft()
        visited_nodes.append(new_node)
        drone(new_node)
        goback = 2
    print("Se acabó lo que se daba")    


def SecondAlgorithm() -> Generator[tuple[int, int], None, None]:
    available_nodes: list[node] = []
    visited_nodes: list[node] = []

    new_node: node = a
    visited_nodes.append(a)
    yield (new_node)

    goback:int = 2
    while (new_node.exit is False):
        available_nodes = [node for node in new_node.connections if node not in visited_nodes]
        if not available_nodes:
            path : list[node] = visited_nodes.copy()
            new_node = path[-goback]
            yield (new_node)
            goback += 1
            continue
        av_node = deque(available_nodes)
        new_node = av_node.popleft()
        visited_nodes.append(new_node)
        yield (new_node)
        goback = 2
    print("Se acabó lo que se daba")
        

def ThirdAlgorithm() -> Generator[tuple[int, int], None, None]:
    available_nodes: list[node] = []
    visited_nodes: list[node] = []

    new_node: node = a
    visited_nodes.append(a)
    yield (new_node)

    goback:int = 2
    while (new_node.exit is False):
        available_nodes = [node for node in new_node.connections if node not in visited_nodes]
        if not available_nodes:
            path : list[node] = visited_nodes.copy()
            new_node = path[-goback]
            yield (new_node)
            goback += 1
            continue
        av_node = deque(available_nodes)
        new_node = av_node.popleft()
        visited_nodes.append(new_node)
        yield (new_node)
        goback = 2
    print("Se acabó lo que se daba")


def main() -> None:
    algorithm = SecondAlgorithm()

    while True:
        input("Press Enter to move the drone...")

        try:
            current_node = next(algorithm)
            print(
                f"Drone is at node {current_node.name} in positions: "
                f"({current_node.x}, {current_node.y})"
            )
        except StopIteration:
            print("The drone has reached the exit")
            break


if __name__ == "__main__":
    main()
     
    
"""
for node in nodes:
print(
    node.name,
    (node.x, node.y),
    "entry:", node.entry,
    "exit:", node.exit,
    "connections:", node.connections,
)
"""

