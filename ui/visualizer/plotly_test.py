from .base import Visualizer

from plotly.graph_objects import (
    Figure, Scatter, Layout, Marker, Line)

class plotlyzer(Visualizer):
     def create_visualization(self,
        turn_movements: dict[int, list[MovementRecord]]) -> None
        pass

