"""Abstract Plotly visualizer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from DroneGen.base import MovementRecord
from DroneGen.Graph.Map import Graph

if TYPE_CHECKING:
    from plotly.graph_objects import Figure


class Visualizer(ABC):
    """Convert a Fly-in graph and movement history into a Plotly figure."""

    def __init__(self, graph: Graph) -> None:
        """Store the graph's static geometry."""
        self.graph = graph

    @abstractmethod
    def create_visualization(
        self,
        turn_movements: dict[int, list[MovementRecord]],
    ) -> Figure:
        """Render the complete simulation without changing engine state."""
        raise NotImplementedError
