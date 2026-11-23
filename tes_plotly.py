"""Manual smoke test for rendering one static Fly-in map as HTML."""

from DroneGen.Graph.MapFactory import Factory
from input.receiver import receiver
from ui.visualizer.plotly_test import plotlyzer


def main() -> None:
    """Export the priority map without opening a browser process."""
    model = receiver("maps/medium/03_priority_puzzle.txt").Process()
    if model is None:
        raise ValueError("Unable to read priority map")

    graph = Factory().create_graph(
        hubs=model.HUBS,
        connections=model.CONNECTIONS,
    )
    plotlyzer(graph).create_figure().write_html(
        "flyin_preview.html", auto_open=False
    )


if __name__ == "__main__":
    main()
