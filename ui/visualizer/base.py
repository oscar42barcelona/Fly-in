from __future__ import annotations

from DroneGen.base import MovementRecord
from DroneGen.Graph.Map import Node, Connection, Graph
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotly.graph_objects import Figure


class Visualizer(ABC):

    def __init__(
        self,
        graph: Graph,
    ) -> None:
        #self.node = node
        #self.connection = connection
        self.graph = graph

    @abstractmethod
    def create_visualization(self, 
        turn_movements: dict[int, list[MovementRecord]]) -> Figure:
        pass
