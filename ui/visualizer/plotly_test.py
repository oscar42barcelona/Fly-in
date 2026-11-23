"""Plotly map and turn-by-turn drone playback for Fly-in.

The Figure is built from the graph and movement history without mutating them.
It can be saved as HTML now and embedded in Streamlit later.
"""

from __future__ import annotations

from plotly.graph_objects import Figure, Frame, Scatter

from DroneGen.Graph.Map import Connection, Node
from .turn_positions import TurnPositionReplayer

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
    ) -> Figure:
        """Build an interactive Figure with one snapshot per simulation turn."""
        positions = TurnPositionReplayer(self.graph).replay(turn_movements)
        final_turn = max(positions)
        figure = self.create_figure()

        drone_trace_index = len(figure.data)
        figure.add_trace(self._drone_trace(positions[0]))
        figure.frames = [
            Frame(
                name=str(turn),
                data=[self._drone_trace(snapshot)],
                traces=[drone_trace_index],
                layout=dict(title=f"Fly-in | Turn {turn} / {final_turn}"),
            )
            for turn, snapshot in positions.items()
        ]
        figure.update_layout(
            title=f"Fly-in | Turn 0 / {final_turn}",
            margin=dict(l=35, r=35, b=115, t=55),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    showactive=False,
                    x=0.09,
                    xanchor="right",
                    y=-0.12,
                    yanchor="top",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                dict(
                                    frame=dict(duration=650, redraw=True),
                                    transition=dict(duration=0),
                                    fromcurrent=True,
                                    mode="immediate",
                                ),
                            ],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                dict(
                                    frame=dict(duration=0, redraw=False),
                                    transition=dict(duration=0),
                                    mode="immediate",
                                ),
                            ],
                        ),
                    ],
                )
            ],
            sliders=[
                dict(
                    active=0,
                    x=0.17,
                    len=0.81,
                    y=-0.12,
                    currentvalue=dict(prefix="Turn "),
                    steps=[
                        dict(
                            label=str(turn),
                            method="animate",
                            args=[
                                [str(turn)],
                                dict(
                                    frame=dict(duration=0, redraw=True),
                                    transition=dict(duration=0),
                                    mode="immediate",
                                ),
                            ],
                        )
                        for turn in positions
                    ],
                )
            ],
        )
        return figure

    @staticmethod
    def _drone_trace(positions: dict[int, Node | Connection]) -> Scatter:
        """Plot drones at nodes or at the midpoint of an occupied connection."""
        groups: dict[Node | Connection, list[int]] = {}
        for drone_id, place in sorted(positions.items()):
            groups.setdefault(place, []).append(drone_id)

        xs: list[float] = []
        ys: list[float] = []
        labels: list[str] = []
        descriptions: list[str] = []
        colors: list[str] = []

        for place, drone_ids in groups.items():
            if isinstance(place, Connection):
                x, y = place.get_midpoint()
                name = f"{place.node_a.name}-{place.node_b.name} (in transit)"
                color = "#fb923c"
            else:
                x, y = place.x, place.y
                name = place.name
                color = "#38bdf8"

            columns = min(4, len(drone_ids))
            rows = (len(drone_ids) + columns - 1) // columns
            for index, drone_id in enumerate(drone_ids):
                column = index % columns
                row = index // columns
                # A single drone uses the exact node or connection midpoint.
                xs.append(x + (column - (columns - 1) / 2) * 0.10)
                ys.append(y - (row - (rows - 1) / 2) * 0.10)
                labels.append(f"D{drone_id}")
                descriptions.append(name)
                colors.append(color)

        return Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            name="Drones",
            text=labels,
            textposition="top center",
            textfont=dict(size=11, color="#f8fafc"),
            customdata=descriptions,
            hovertemplate="%{text}<br>Position: %{customdata}<extra></extra>",
            marker=dict(
                color=colors,
                size=13,
                line=dict(color="#f8fafc", width=1),
            ),
            showlegend=False,
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
