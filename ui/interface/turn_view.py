"""Present one Plotly turn under Streamlit's playback controls."""

from __future__ import annotations

from copy import deepcopy

from plotly.graph_objects import Figure


def figure_at_turn(figure: Figure, turn: int) -> Figure:
    """Return an independent static snapshot, without inert Plotly controls.

    Keep the original animated figure intact so cached frames remain reusable
    while Streamlit advances or rewinds the turn.
    """
    if not 0 <= turn < len(figure.frames):
        raise IndexError(f"Unknown simulation turn: {turn}")

    selected = deepcopy(figure)
    frame = selected.frames[turn]
    selected.data[-1].update(frame.data[0].to_plotly_json())

    # update_layout(sliders=[], updatemenus=[]) MERGES with existing arrays;
    # direct assignment actually removes the controls from the Plotly figure.
    selected.frames = ()
    selected.layout.sliders = ()
    selected.layout.updatemenus = ()
    selected.update_layout(
        title=f"Fly-in | Turno {turn}",
        margin=dict(l=35, r=35, b=35, t=55),
    )
    return selected
