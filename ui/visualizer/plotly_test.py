from .base import Visualizer

from plotly.graph_objects import (
    Figure, Scatter, Layout, Marker, Line)

class plotlyzer(Visualizer):
     def create_visualization(self,
        turn_movements: dict[int, list[MovementRecord]]) -> None
        pass

    def create_figure(self) -> None:
        fig = Figure()

        fig.add_trace(
            Scatter(
            x=[(node.x for node in self.graph.nodes)],
            y=[(node.y for node in self.graph.nodes)],
            mode="markers+text",
            text=[(node.name for node in self.graph.nodes)],
            textposition="top center",
            hovertemplate=(
                "Nombre: %{text}<br>"
                "X: %{x}<br>"
                "Y: %{y}<extra></extra>"
        )

        for line in self.graph.connections:
            fig.add_trace(
                    Scatter(
                    x=[line.node_a.x, line.node_b.x],
                    y=[line.node_a.y, line.node_b.y],
                    mode="lines",
                    name=f"{node_a.name}-{node_b.name}"
                    ))

        #falta revisar con chat, poner el layout, y sincronizar a ver que sale, hasta manyana!
                 


