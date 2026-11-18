from .base import Visualizer
from DroneGen.base import MovementRecord

from plotly.graph_objects import (
    Figure, Scatter, Layout, Marker, Line)

class plotlyzer(Visualizer):
    def create_visualization(self,
        turn_movements: dict[int, list[MovementRecord]]) -> None:
        pass

    def create_figure(self) -> Figure:
        fig = Figure()

        fig.add_trace(
            Scatter(
            x=[node.x for node in self.graph.nodes],
            y=[node.y for node in self.graph.nodes],
            mode="markers+text",
            text=[node.name for node in self.graph.nodes],
            textposition="top center",
            hovertemplate=(
                "Nombre: %{text}<br>"
                "X: %{x}<br>"
                "Y: %{y}<extra></extra>"
        )))

        for line in self.graph.connections:
            fig.add_trace(
                    Scatter(
                    x=[line.node_a.x, line.node_b.x],
                    y=[line.node_a.y, line.node_b.y],
                    mode="lines",
                    name=f"{line.node_a.name}-{line.node_b.name}"
                    ))

        fig.update_layout(
            title="Visualización del mapa",
            xaxis_title="Coordenada X",
            yaxis_title="Coordenada Y",
            showlegend=False,
            hovermode="closest",
            template="plotly_dark",
            width=1200,
            height=800
            )

        return fig

        #falta revisar con chat, poner el layout, y sincronizar a ver que sale, hasta manyana!
                 


