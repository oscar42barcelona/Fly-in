"""Plotly map rendering tests using validated Fly-in maps."""

from pathlib import Path

import pytest

from DroneGen.Graph.MapFactory import Factory
from input.receiver import receiver
from input.validator import Map_
from ui.visualizer.plotly_test import plotlyzer

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "filename",
    [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/medium/03_priority_puzzle.txt",
    ],
)
def test_figure_draws_connections_before_nodes(filename: str) -> None:
    """Preserve map geometry and keep zones visible over connections."""
    model = Map_.model_validate(
        receiver().slicer(
            (ROOT / filename).read_text(encoding="utf-8").splitlines()
        )
    )
    graph = Factory().create_graph(model.HUBS, model.CONNECTIONS)
    figure = plotlyzer(graph).create_figure()

    assert len(figure.data) == len(graph.connections) + 1
    for trace, connection in zip(figure.data[:-1], graph.connections):
        assert trace.mode == "lines"
        assert list(trace.x) == [connection.node_a.x, connection.node_b.x]
        assert list(trace.y) == [connection.node_a.y, connection.node_b.y]
        assert str(connection.capacity) in trace.text[0]

    zones = figure.data[-1]
    assert zones.mode == "markers+text"
    assert list(zones.x) == [node.x for node in graph.nodes]
    assert list(zones.y) == [node.y for node in graph.nodes]
    assert list(zones.text) == [node.name for node in graph.nodes]
    assert list(zones.customdata) == [
        [node.type.value, node.zone.value, node.capacity]
        for node in graph.nodes
    ]
    assert figure.layout.yaxis.scaleanchor == "x"
    assert figure.layout.yaxis.scaleratio == 1
    assert figure.layout.autosize


def test_priority_and_restricted_zones_have_distinct_metadata() -> None:
    """Represent zone types and custom colors in the Plotly figure."""
    path = ROOT / "maps/medium/03_priority_puzzle.txt"
    model = Map_.model_validate(
        receiver().slicer(path.read_text(encoding="utf-8").splitlines())
    )
    graph = Factory().create_graph(model.HUBS, model.CONNECTIONS)
    zones = plotlyzer(graph).create_figure().data[-1]

    categories = {row[1] for row in zones.customdata}
    assert "priority" in categories
    assert "restricted" in categories
    names = list(zones.text)
    restricted_index = names.index("slow_path1")
    assert zones.marker.color[restricted_index] == "red"


def test_figure_can_be_serialized_without_browser() -> None:
    """The same Figure can later be passed directly to Streamlit."""
    path = ROOT / "maps/easy/01_linear_path.txt"
    model = Map_.model_validate(
        receiver().slicer(path.read_text(encoding="utf-8").splitlines())
    )
    graph = Factory().create_graph(model.HUBS, model.CONNECTIONS)
    figure = plotlyzer(graph).create_figure()
    data = figure.to_plotly_json()
    assert len(data["data"]) == len(graph.connections) + 1
    assert data["layout"]["template"]
