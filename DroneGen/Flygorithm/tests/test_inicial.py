from __future__ import annotations
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
b.connect(d)
c.connect(d)
d.connect(e)

b.connect(f)
f.connect(g)

nodes = [a, b, c, d, e, f, g]

def FirstAlgorithm():
    #drone = (a.x, a.y)
    visited_nodes: list[node] = []
    movements: int = 0

    new_node = a
    for i in range(5):
        prev_node = deque(new_node.connections)
        new_node = prev_node.popleft()
        print(f"Drone is at {new_node.name}")
        
        
        
        
        

if __name__ == "__main__":
    FirstAlgorithm()





"""
for node in nodes:
    print(
        node.name,
        (node.x, node.y),
        "entry:", node.entry,
        "exit:", node.exit,
        "connections:", node.connections,
    )"""
