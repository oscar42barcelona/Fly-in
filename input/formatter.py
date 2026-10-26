from .validator import Hub, Map_
from pathlib import Path
from .receiver import receiver

from DroneGen.Graph.MapFactory import Factory


control = receiver()
dicforpy = control.Process()
if dicforpy:
    modelo_py = Map_.model_validate(dicforpy, extra="forbid")




#En primer lugar instancio factory
factory = factory()

#En segundo lugar vemos que bola
graph = factory.create_graph(hubs=modelo_py.HUBS, 
                            connections=modelo_py)

print("\n=== GRAPH ===")

for name, value in vars(graph).items():
    print(f"\n{name}:")

    if isinstance(value, list):
        print(f"Total: {len(value)}")

        for i, obj in enumerate(value, start=1):
            print(f"\n  Elemento {i}:")
