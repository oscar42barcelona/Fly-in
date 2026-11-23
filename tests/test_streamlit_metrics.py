"""Service and UI regression tests for Streamlit turn metrics."""

from pathlib import Path

import pytest

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
        str(ROOT / "tes_streamlit_turnos.py"), default_timeout=20
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
