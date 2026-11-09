from .validator import Hub, Map_
from pathlib import Path
from .receiver import receiver

from DroneGen.Graph.MapFactory import Factory


control = receiver()
dicforpy = control.Process()
if dicforpy:
    modelo_py = Map_.model_validate(dicforpy, extra="forbid")




#En primer lugar instancio factory
factory = Factory()

#En segundo lugar vemos que bola
graph = factory.create_graph(hubs=modelo_py.HUBS, 
                            connections=modelo_py.CONNECTIONS)

drones_list = factory.create_drones(nb_drones=modelo_py.NB_DRONES,
                                    start_node=modelo_py.START_HUB)

print("=== NODES ===")
for node in graph.nodes:
    print(vars(node))

print("\n=== CONNECTIONS ===")
for connection in graph.connections:
    print(vars(connection))

print("\n=== Drones ===")
for drone in drones_list:
    print(vars(drone))