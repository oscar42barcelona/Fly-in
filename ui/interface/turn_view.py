"""Render a single simulation turn as a static Plotly figure."""

from __future__ import annotations

from copy import deepcopy

from plotly.graph_objects import Figure


class TurnFigureView:
    """Select a frame without altering the cached animated Figure."""

    def __init__(self, figure: Figure) -> None:
        """Store the original animation as read-only source data."""
        self.figure = figure

    def at_turn(self, turn: int) -> Figure:
        """Return a snapshot without the inactive Plotly playback controls."""
        if not 0 <= turn < len(self.figure.frames):
            raise IndexError(f"Unknown simulation turn: {turn}")

        selected = deepcopy(self.figure)
        frame = selected.frames[turn]
        selected.data[-1].update(frame.data[0].to_plotly_json())

        # Direct assignment removes the controls; update_layout merges arrays.
        selected.frames = ()
        selected.layout.sliders = ()
        selected.layout.updatemenus = ()
        selected.update_layout(
            title=f"Fly-in | Turn {turn}",
            margin=dict(l=35, r=35, b=35, t=55),
        )
        return selected
