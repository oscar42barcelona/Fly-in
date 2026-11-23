"""Plotly animation tests driven by actual Fly-in movement records."""

from pathlib import Path

import pytest

from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Graph.Map import Node
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Orchestrator import orchestrator
from input.receiver import receiver
from input.validator import HubType, Map_
from ui.visualizer.plotly_test import plotlyzer
from ui.visualizer.turn_positions import TurnPositionReplayer

ROOT = Path(__file__).resolve().parents[1]


def build_simulation(map_text: str):
    model = Map_.model_validate(receiver().slicer(map_text.splitlines()))
    graph = Factory().create_graph(model.HUBS, model.CONNECTIONS)
    start = next(node for node in graph.nodes if node.type == HubType.ENTRY)
    drones = Factory().create_drones(model.NB_DRONES, start)
    routes = Algorithm().solve(drones[0], graph, model.NB_DRONES)
    movements = orchestrator().plan(drones, routes, graph)
    return graph, drones, movements


@pytest.mark.parametrize(
    "filename",
    [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/easy/03_basic_capacity.txt",
        "maps/medium/03_priority_puzzle.txt",
    ],
)
def test_animation_tracks_every_drone(filename: str) -> None:
    graph, drones, movements = build_simulation(
        (ROOT / filename).read_text(encoding="utf-8")
    )
    occupancy_before = {
        node: tuple(node.drones) for node in graph.nodes
    }
    states = TurnPositionReplayer(graph).replay(movements)
    figure = plotlyzer(graph).create_visualization(movements)

    assert len(states) == len(movements) + 1
    assert len(figure.frames) == len(states)
    assert figure.frames[0].name == "0"
    assert len(figure.layout.sliders[0].steps) == len(states)
    assert len(figure.layout.updatemenus[0].buttons) == 2
    assert set(states[0]) == {drone.id for drone in drones}
    assert all(
        position.type == HubType.ENTRY for position in states[0].values()
    )
    assert all(
        position.type == HubType.EXIT
        for position in states[max(states)].values()
    )

    # Rendering must not change the state that the orchestrator produced.
    assert {
        node: tuple(node.drones) for node in graph.nodes
    } == occupancy_before
    for frame in figure.frames:
        assert len(frame.data[0].x) == len(drones)
        assert len(set(frame.data[0].text)) == len(drones)


def test_restricted_transit_uses_connection_midpoint() -> None:
    text = """
nb_drones: 1
start_hub: start 0 0
hub: restricted 1 -1 [zone=restricted]
end_hub: goal 2 0
connection: start-restricted
connection: restricted-goal
"""
    graph, drones, movements = build_simulation(text)
    connection = next(
        edge for edge in graph.connections
        if edge.node_a.name == "start"
    )
    assert connection.get_midpoint() == (0.5, -0.5)

    positions = TurnPositionReplayer(graph).replay(movements)
    drone_id = drones[0].id
    assert positions[1][drone_id] is connection
    assert isinstance(positions[2][drone_id], Node)
    assert positions[2][drone_id].name == "restricted"

    figure = plotlyzer(graph).create_visualization(movements)
    transit = figure.frames[1].data[0]
    assert list(transit.x) == [0.5]
    assert list(transit.y) == [-0.5]
    assert list(transit.text) == [f"D{drone_id}"]
    assert "in transit" in transit.customdata[0]

    arrival = figure.frames[2].data[0]
    assert list(arrival.x) == [1]
    assert list(arrival.y) == [-1]


def test_waiting_drones_remain_at_last_position() -> None:
    path = ROOT / "maps/easy/01_linear_path.txt"
    graph, drones, movements = build_simulation(
        path.read_text(encoding="utf-8")
    )
    positions = TurnPositionReplayer(graph).replay(movements)
    assert positions[0][drones[1].id] is positions[1][drones[1].id]


def test_html_playback_is_self_contained(tmp_path: Path) -> None:
    path = ROOT / "maps/easy/01_linear_path.txt"
    graph, _, movements = build_simulation(path.read_text(encoding="utf-8"))
    html_path = tmp_path / "playback.html"
    plotlyzer(graph).create_visualization(movements).write_html(
        html_path, auto_open=False
    )
    page = html_path.read_text(encoding="utf-8")
    assert "Plotly" in page
    assert "D1" in page
    assert "Play" in page


def test_cli_visualize_calls_plotly_figure(monkeypatch) -> None:
    """No graphical display is needed to verify the CLI integration."""
    from plotly.graph_objects import Figure

    from input.formatter_algorithm_integrado import main

    output = {}

    def fake_write_html(self, filename, auto_open=False):
        output["filename"] = filename
        output["auto_open"] = auto_open
        output["frames"] = len(self.frames)

    monkeypatch.setattr(Figure, "write_html", fake_write_html)
    main(str(ROOT / "maps/easy/01_linear_path.txt"), visualize=True)

    assert output == {
        "filename": "flyin_preview.html",
        "auto_open": False,
        "frames": 5,
    }
