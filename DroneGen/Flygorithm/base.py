from abc import ABC
from ..Graph.Drone import Drone
from ..Graph.Map import Graph
from enum import Enum
from dataclasses import dataclass


class State(Enum):
    """
    MOVEMENT = Movimiento hacia otro nodo, incluido end_hub
    TRANSIT = Dron en tránsito hacia una zona restricted
    STAY = Dron que permanece en el mismo nodo
    """
    MOVEMENT = "movement"
    TRANSIT = "transit"
    STAY = "stay"


@dataclass(frozen=True)
class MovementRecord:
    """
    drone_id = Identificador del dron
    state = Situación registrada
    location = Identificador del nodo o conexión
    """
    drone_id: int
    state: State
    location: str    


class flygorithm(ABC):
    """Este algorimto debe de encargarse de transportar
        los drones desde start_hub hasta end_hub"""
    @abstractmethod
    def solve(drones: list[Drone], graph: Graph) -> dict[int, list[MovementRecord]]
        """Parametros:
            - drones: Drones que participarán en la simulación.
            - Map: Objeto que contiene la red, conexiones y restricciones.
        salida:
            - diccionario donde cada clave representa un turno 
            y cada valor contiene los registros correspondientes.
        error:
            si no existe una ruta posible desde el inicio hasta el destino
        """
        ...
