"""Plotly representation of Fly-in's static map geometry.

A graph is rendered from its coordinates without changing simulation state.
The turn-by-turn drone layer will be added separately.
"""

from __future__ import annotations

from plotly.graph_objects import Figure, Scatter

from .base import Visualizer
from DroneGen.base import MovementRecord
from input.validator import HubType, Zone


_ZONE_COLORS = {
    Zone.NORMAL: "#60a5fa",
    Zone.RESTRICTED: "#f59e0b",
    Zone.PRIORITY: "#34d399",
    Zone.BLOCKED: "#94a3b8",
}


class plotlyzer(Visualizer):
    def create_visualization(
        self, turn_movements: dict[int, list[MovementRecord]]
    ) -> None:
        """The turn-by-turn visual layer is not implemented yet."""
        raise NotImplementedError(
            "Turn playback is not implemented; use create_figure() for the map"
        )

    def create_figure(self) -> Figure:
        """Draw map connections and zones using graph x/y coordinates."""
        fig = Figure()

        # Lines go first so that zone markers remain visible on top.
        for connection in self.graph.connections:
            a, b = connection.node_a, connection.node_b
            fig.add_trace(
                Scatter(
                    x=[a.x, b.x],
                    y=[a.y, b.y],
                    mode="lines",
                    name=f"{a.name}-{b.name}",
                    line=dict(color="#64748b", width=2),
                    text=[
                        f"{a.name} - {b.name}<br>Capacity: {connection.capacity}"
                    ] * 2,
                    hovertemplate="%{text}<extra></extra>",
                    showlegend=False,
                )
            )

        nodes = self.graph.nodes
        colors = []
        symbols = []
        for node in nodes:
            if node.type == HubType.ENTRY:
                colors.append("#22c55e")
                symbols.append("diamond")
            elif node.type == HubType.EXIT:
                colors.append("#ef4444")
                symbols.append("square")
            else:
                colors.append(
                    node.COLOR if node.COLOR and node.COLOR != "grey"
                    else _ZONE_COLORS[node.zone]
                )
                symbols.append("circle")

        fig.add_trace(
            Scatter(
                x=[node.x for node in nodes],
                y=[node.y for node in nodes],
                mode="markers+text",
                name="Zones",
                text=[node.name for node in nodes],
                textposition="top center",
                customdata=[
                    [node.type.value, node.zone.value, node.capacity]
                    for node in nodes
                ],
                hovertemplate=(
                    "Zone: %{text}<br>"
                    "Type: %{customdata[0]}<br>"
                    "Category: %{customdata[1]}<br>"
                    "Capacity: %{customdata[2]}<extra></extra>"
                ),
                marker=dict(
                    color=colors,
                    symbol=symbols,
                    size=19,
                    line=dict(color="#e2e8f0", width=1),
                ),
                showlegend=False,
            )
        )

        fig.update_layout(
            title="Fly-in | Map",
            xaxis_title="X",
            yaxis_title="Y",
            xaxis=dict(zeroline=False, showgrid=True),
            yaxis=dict(zeroline=False, showgrid=True, scaleanchor="x", scaleratio=1),
            showlegend=False,
            hovermode="closest",
            template="plotly_dark",
            autosize=True,
            margin=dict(l=35, r=35, b=35, t=55),
        )
        return fig
