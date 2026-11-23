"""Service, playback, and Streamlit regression tests."""

from pathlib import Path

import pytest

from ui.interface.app import FlyInApp, PlaybackController
from ui.interface.turn_view import TurnFigureView
from ui.visualizer.simulation_service import (
    SimulationData,
    SimulationService,
    TurnMetrics,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("relative_path", "drone_count"),
    [
        ("maps/easy/01_linear_path.txt", 2),
        ("maps/easy/02_simple_fork.txt", 4),
        ("maps/easy/03_basic_capacity.txt", 4),
        ("maps/medium/01_dead_end_trap.txt", 5),
        ("maps/medium/02_circular_loop.txt", 6),
        ("maps/medium/03_priority_puzzle.txt", 5),
        ("maps/hard/01_maze_nightmare.txt", 8),
        ("maps/hard/02_capacity_hell.txt", 12),
        ("maps/hard/03_ultimate_challenge.txt", 15),
    ],
)
def test_service_returns_every_turn(
    relative_path: str, drone_count: int
) -> None:
    """Verify all simulation turns and final delivery counts."""
    result = SimulationService(str(ROOT / relative_path)).build()
    metrics = result.metrics
    total = result.total_drones

    assert isinstance(result, SimulationData)
    assert total == drone_count
    assert list(metrics) == list(range(len(result.figure.frames)))
    assert metrics[0] == TurnMetrics(delivered=0, transit=0, waiting=0)
    assert metrics[max(metrics)].delivered == total
    assert metrics[max(metrics)].transit == 0
    assert metrics[max(metrics)].waiting == 0
    assert all(
        0 <= item.delivered + item.transit + item.waiting <= total
        for item in metrics.values()
    )


def test_waiting_drones_are_counted_from_history() -> None:
    """Only drones not moving in the current turn count as waiting."""
    result = SimulationService(
        str(ROOT / "maps/easy/01_linear_path.txt")
    ).build()
    assert result.metrics[1].waiting == 1
    assert result.metrics[1].transit == 0
    assert result.metrics[1].delivered == 0


def test_restricted_link_is_counted_as_transit(tmp_path: Path) -> None:
    """A drone at a restricted midpoint counts as in transit."""
    path = tmp_path / "restricted.txt"
    path.write_text(
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: restricted 2 0 [zone=restricted]",
                "end_hub: goal 4 0",
                "connection: start-restricted",
                "connection: restricted-goal",
            ]
        ),
        encoding="utf-8",
    )

    result = SimulationService(str(path)).build()
    assert result.total_drones == 1
    assert result.metrics[1] == TurnMetrics(0, 1, 0)
    assert result.metrics[2] == TurnMetrics(0, 0, 0)
    assert result.metrics[3] == TurnMetrics(1, 0, 0)
    assert list(result.figure.frames[1].data[0].x) == [1.0]


def test_playback_controller_boundaries() -> None:
    """Manual navigation and automatic playback never exceed the limits."""
    controller = PlaybackController()
    controller.previous()
    assert controller.turn == 0

    controller.start(last_turn=2)
    assert controller.playing
    controller.tick(last_turn=2)
    assert controller.turn == 1
    controller.tick(last_turn=2)
    assert controller.turn == 2
    assert not controller.playing

    controller.next(last_turn=2)
    assert controller.turn == 2
    controller.previous()
    assert controller.turn == 1


def test_turn_view_hides_plotly_controls() -> None:
    """The rendered copy has no stale animation controls."""
    result = SimulationService(
        str(ROOT / "maps/easy/01_linear_path.txt")
    ).build()
    figure = result.figure
    frame_count = len(figure.frames)
    selected = TurnFigureView(figure).at_turn(1)

    assert selected is not figure
    assert not selected.frames
    assert not selected.layout.sliders
    assert not selected.layout.updatemenus
    assert selected.layout.title.text == "Fly-in | Turn 1"
    assert list(selected.data[-1].x) == list(figure.frames[1].data[0].x)
    assert len(figure.frames) == frame_count
    assert len(figure.layout.sliders) == 1


def test_map_selector_lists_all_bundled_maps_by_difficulty() -> None:
    """Show every map in sorted category order, without demo entries."""
    available = FlyInApp.available_maps()
    assert list(available) == [
        "Easy / 01 Linear Path",
        "Easy / 02 Simple Fork",
        "Easy / 03 Basic Capacity",
        "Medium / 01 Dead End Trap",
        "Medium / 02 Circular Loop",
        "Medium / 03 Priority Puzzle",
        "Hard / 01 Maze Nightmare",
        "Hard / 02 Capacity Hell",
        "Hard / 03 Ultimate Challenge",
        "Challenger / 01 The Impossible Dream",
    ]
    assert len(set(available.values())) == 10
    assert all((ROOT / path).is_file() for path in available.values())
    assert all("demo" not in path for path in available.values())


def test_app_shows_english_controls_and_metrics() -> None:
    """The Streamlit interface retains navigation across reruns."""
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        str(ROOT / "ui/interface/app.py"), default_timeout=20
    ).run()
    assert not app.exception
    assert app.selectbox[0].label == "Select a map"
    assert list(app.selectbox[0].options) == list(
        FlyInApp.available_maps()
    )
    assert [button.label for button in app.button] == [
        "Previous", "Next", "Play", "Pause"
    ]
    assert [item.label for item in app.metric] == [
        "Delivered", "In transit", "Waiting"
    ]
    assert app.metric[0].value == "0 / 2"
    assert app.metric[1].value == "0"
    assert app.metric[2].value == "0"

    app.button[1].click().run()
    assert not app.exception
    assert app.metric[2].value == "1"

    app.selectbox[0].set_value("Medium / 03 Priority Puzzle").run()
    assert not app.exception
    assert app.metric[0].value == "0 / 5"


def test_streamlit_play_and_pause_update_controller() -> None:
    """Auto playback advances and Pause freezes the current turn."""
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        str(ROOT / "ui/interface/app.py"), default_timeout=20
    ).run()
    assert not app.exception

    app.button[2].click().run()
    assert not app.exception
    state = app.session_state["playback"]
    assert state.playing
    assert state.turn == 1

    app.button[3].click().run()
    assert not app.exception
    state = app.session_state["playback"]
    assert not state.playing
    assert state.turn == 1

    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["playback"].turn == 2
