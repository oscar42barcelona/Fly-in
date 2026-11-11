from .validator import Hub, Map_
from pathlib import Path
from .receiver import receiver

from DroneGen.Graph.MapFactory import Factory
from DroneGen.Flygorithm.Algorithm import Algorithm


control = receiver()
dicforpy = control.Process()
alg = Algorithm()

if dicforpy:
    modelo_py = Map_.model_validate(dicforpy, extra="forbid")




#En primer lugar instancio factory
factory = Factory()

#En segundo lugar vemos que bola
graph = factory.create_graph(hubs=modelo_py.HUBS, 
                            connections=modelo_py.CONNECTIONS)

for node in graph.nodes:
     if node.type == "entry":
        start = node


drones_list = factory.create_drones(nb_drones=modelo_py.NB_DRONES,
                                    start_node=start)
drone = drones_list[0]

solution_route = alg.djikstra_route_finding(drone, graph)

print("\n=== Solution ===")
for node in solution_route:
    print(vars(drone))




"""
print("=== NODES ===")
for node in graph.nodes:
    print(vars(node))

print("\n=== CONNECTIONS ===")
for connection in graph.connections:
    print(vars(connection))

print("\n=== Drones ===")
for drone in drones_list:
    print(vars(drone))"""
