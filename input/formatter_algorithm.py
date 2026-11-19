from .validator import Hub, Map_
from pathlib import Path
from .receiver import receiver

from DroneGen.Graph.MapFactory import Factory
from DroneGen.Orchestrator import orchestrator
from DroneGen.Flygorithm.Algorithm import Algorithm
from ui.visualizer.render_tester import launch

#from ui.visualizer.plotly_test import plotlyzer


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

solution = alg.solve(drone, graph, modelo_py.NB_DRONES)


cli = orchestrator()

turn_movements = cli.plan(drones_list, solution, graph)

for turn, movements in turn_movements.items():
    print(f"TURN {turn}")
    for movement in movements:
        print(
            movement.drone_id,
            movement.state,
            movement.location
        )
print(
    turn_movements[1] is turn_movements[2]
)

launch(graph, turn_movements, start_name="hub")


















"""
for node in graph.nodes:
     if node.type == "entry":
        start = node


drones_list = factory.create_drones(nb_drones=modelo_py.NB_DRONES,
                                    start_node=start)
drone = drones_list[0]

solution = alg.solve(drone, graph, modelo_py.NB_DRONES)



print("\n=== Solution ===")

for i, (cost, complete_route) in enumerate(solution, start=1):
    print(f"\nRuta {i}")
    print(f"Coste: {cost}")
    print("Recorrido:", " -> ".join(n.name for n in complete_route))

print("=== NODES ===")
for node in graph.nodes:
    print(vars(node))

print("\n=== CONNECTIONS ===")
for connection in graph.connections:
    print(vars(connection))

print("\n=== Drones ===")
for drone in drones_list:
    print(vars(drone))"""
