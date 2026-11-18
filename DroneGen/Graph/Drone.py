from typing import TYPE_CHECKING
from ..Graph.base import State 

if TYPE_CHECKING:
    from .Map import Node, Connection, Drone, Graph

class Drone:
    def __init__(self, id_: int,
                start_node: Node):
        self.id = id_
        self.current_node: Node | None = start_node
        self.current_connection: Connection | None = None
        self.headed_to: Node | None = None
        self.delivered: bool = False
        self.state: State = State.STAY
        self.current_route = 0

    def move_to_node(self, destination: Node) -> None:
        """actualizar la posición en un movimiento de un 
        turno hacia zona normal o priority."""

        if destination = self.current_node:
            self.state = State.STAY
            return        
    
        self.current_node = destination

        self.state = State.MOVEMENT

        """errores: (InvalidDroneStateError)"""

    def start_restricted_transit(self, connection: Connection,
                                destination: Node) -> None:
        """reflejar el inicio de un movimiento que requiere dos turnos."""
        self.current_connection = connection
        self.current_node = None
        self.state = State.TRANSIT
        self.headed_to = destination
        """Errores: estado inválido mediante mecanismo aún por cerrar."""

    def end_restricted_transit() -> None:
        """reflejar la llegada obligatoria al 
            término del segundo turno."""

        self.current_connection = None
        self.current_node = self.headed_to
        self.headed_to = None

        """Errores: estado inválido mediante 
            mecanismo aún por cerrar"""
                                           
