def atob():
    node = a
    drone = node.name
    visited_nodes = [node]

    print(f"Drone is at {drone}: {node.x}, {node.y} location")
    print()
    print("Moving to the next node")

    node = node.connections[0]
    drone = node.name
    visited_nodes.append(node)
    print(f"Drone is at {drone}: {node.x}, {node.y} location")

    if node.connections[0] in visited_nodes:
        node = node.connections[1]
        drone = node.name

    visited_nodes.append(node)
    print("Moving to the next node")
    print(f"Drone is at {drone}: {node.x}, {node.y} location")

    if node.connections[0] in visited_nodes:
        node = node.connections[1]
        drone = node.name

    visited_nodes.append(node)
    print("Moving to the next node")
    print(f"Drone is at {drone}: {node.x}, {node.y} location")

    if node.connections[0] in visited_nodes:
        node = node.connections[1]
        drone = node.name

    visited_nodes.append(node)
    print("Moving to the next node")
    print(f"Drone is at {drone}: {node.x}, {node.y} location")

    if node.connections[0] and node.connections[1] in visited_nodes:
        node = node.connections[2]
        drone = node.name

    visited_nodes.append(node)
    print("Moving to the next node")
    print(f"Drone is at {drone}: {node.x}, {node.y} location")
