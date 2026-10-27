from __future__ import annotations
from typing import TYPE_CHECKING

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

    def move_to_node(self, destination: Node) -> None:
        """actualizar la posición en un movimiento de un 
        turno hacia zona normal o priority."""
        self.current_node = destination
        """errores: (InvalidDroneStateError)"""

    def start_restricted_transit(self, connection: Connection,
                                destination: Node) -> None:
        """reflejar el inicio de un movimiento que requiere dos turnos."""
        self.current_connection = connection
        self.current_node = None
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
                                           
