"""Service and UI regression tests for Streamlit turn metrics."""

from pathlib import Path

import pytest

from ui.interface.turn_view import figure_at_turn
from ui.visualizer.simulation_service import (
    TurnMetrics,
    build_simulation,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("relative_path", "drone_count"),
    [
        ("maps/easy/01_linear_path.txt", 2),
        ("maps/medium/03_priority_puzzle.txt", 5),
    ],
)
def test_simulation_service_returns_every_turn(
    relative_path: str, drone_count: int
) -> None:
    figure, metrics, total = build_simulation(str(ROOT / relative_path))

    assert total == drone_count
    assert list(metrics) == list(range(len(figure.frames)))
    assert metrics[0] == TurnMetrics(delivered=0, transit=0, waiting=0)
    assert metrics[max(metrics)].delivered == total
    assert metrics[max(metrics)].transit == 0
    assert metrics[max(metrics)].waiting == 0
    assert all(
        0 <= item.delivered + item.transit + item.waiting <= total
        for item in metrics.values()
    )


def test_waiting_drones_are_counted_from_history() -> None:
    _, metrics, _ = build_simulation(
        str(ROOT / "maps/easy/01_linear_path.txt")
    )
    # Two drones start in the same node, but only one can leave in turn one.
    assert metrics[1].waiting == 1
    assert metrics[1].transit == 0
    assert metrics[1].delivered == 0


def test_restricted_link_is_counted_as_transit(tmp_path: Path) -> None:
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

    figure, metrics, count = build_simulation(str(path))
    assert count == 1
    assert metrics[1] == TurnMetrics(delivered=0, transit=1, waiting=0)
    assert metrics[2] == TurnMetrics(delivered=0, transit=0, waiting=0)
    assert metrics[3] == TurnMetrics(delivered=1, transit=0, waiting=0)
    assert list(figure.frames[1].data[0].x) == [1.0]


def test_app_has_controls_and_metrics() -> None:
    """Streamlit AppTest renders the actual page without starting a server."""
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        str(ROOT / "ui/interface/app.py"), default_timeout=20
    ).run()
    assert not app.exception
    assert len(app.metric) == 3
    assert app.metric[0].value == "0 / 2"
    assert app.metric[1].value == "0"
    assert app.metric[2].value == "0"

    app.button[1].click().run()
    assert not app.exception
    assert app.metric[2].value == "1"

    app.selectbox[0].set_value("Mapa de prioridades").run()
    assert not app.exception
    assert app.metric[0].value == "0 / 5"


def test_streamlit_frame_hides_plotly_animation_controls() -> None:
    """Plotly's stale controls should not remain visible in a static frame."""
    figure, _, _ = build_simulation(
        str(ROOT / "maps/easy/01_linear_path.txt")
    )
    frame_count = len(figure.frames)
    selected = figure_at_turn(figure, 1)

    assert selected is not figure
    assert not selected.frames
    assert not selected.layout.sliders
    assert not selected.layout.updatemenus
    assert selected.layout.title.text == "Fly-in | Turno 1"
    assert list(selected.data[-1].x) == list(figure.frames[1].data[0].x)
    # The cached animated Figure is still reusable for further turns.
    assert len(figure.frames) == frame_count
    assert len(figure.layout.sliders) == 1
    assert len(figure.layout.updatemenus) == 1


def test_streamlit_play_and_pause_are_stateful() -> None:
    """Play advances the selected turn; Pause stops automatic playback."""
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        str(ROOT / "ui/interface/app.py"), default_timeout=20
    ).run()
    assert not app.exception
    assert [button.label for button in app.button] == [
        "Anterior", "Siguiente", "Play", "Pause"
    ]

    app.button[2].click().run()
    assert not app.exception
    assert app.session_state["playing"] is True
    assert app.session_state["turno"] == 1

    app.button[3].click().run()
    assert not app.exception
    assert app.session_state["playing"] is False
    assert app.session_state["turno"] == 1

    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["turno"] == 2
