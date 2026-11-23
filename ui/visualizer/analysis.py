"""Aggregate and visualize historical Fly-in simulation metrics.

The input consists only of completed turn metrics. This module neither
re-runs planning nor accesses mutable drone or graph state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from plotly.graph_objects import Figure, Scatter

from ui.visualizer.simulation_service import TurnMetrics


@dataclass(frozen=True)
class SimulationSummary:
    total_drones: int
    total_turns: int
    peak_waiting: int
    total_waiting_drone_turns: int
    peak_transit: int


def summarize_simulation(
    metrics: dict[int, TurnMetrics], total_drones: int
) -> SimulationSummary:
    """Summarize the completed simulation from end-of-turn snapshots."""
    if not metrics or total_drones <= 0:
        raise ValueError("Simulation metrics and drone count must be positive")
    turns = sorted(metrics)
    if turns != list(range(turns[-1] + 1)):
        raise ValueError("Turn metrics must include every turn from zero")
    if metrics[turns[-1]].delivered != total_drones:
        raise ValueError("Cannot summarize an incomplete simulation")

    return SimulationSummary(
        total_drones=total_drones,
        total_turns=turns[-1],
        peak_waiting=max(item.waiting for item in metrics.values()),
        total_waiting_drone_turns=sum(item.waiting for item in metrics.values()),
        peak_transit=max(item.transit for item in metrics.values()),
    )


def create_occupancy_figure(metrics: dict[int, TurnMetrics]) -> Figure:
    """Show the number of waiting and in-transit drones after each turn."""
    turns = sorted(metrics)
    fig = Figure()
    fig.add_trace(
        Scatter(
            x=turns,
            y=[metrics[turn].waiting for turn in turns],
            name="En espera",
            mode="lines+markers",
        )
    )
    fig.add_trace(
        Scatter(
            x=turns,
            y=[metrics[turn].transit for turn in turns],
            name="En tránsito",
            mode="lines+markers",
        )
    )
    fig.update_layout(
        title="Ocupación durante la simulación",
        xaxis_title="Turno",
        yaxis_title="Número de drones",
        yaxis=dict(rangemode="tozero"),
        hovermode="x unified",
        template="plotly_dark",
    )
    return fig


def create_comparison_figure(
    simulations: Mapping[str, tuple[dict[int, TurnMetrics], int]],
) -> Figure:
    """Compare delivered percentages, accounting for different drone counts."""
    if len(simulations) < 2:
        raise ValueError("At least two simulations are required for comparison")

    fig = Figure()
    for name, (metrics, total_drones) in simulations.items():
        summarize_simulation(metrics, total_drones)
        turns = sorted(metrics)
        fig.add_trace(
            Scatter(
                x=turns,
                y=[
                    100 * metrics[turn].delivered / total_drones
                    for turn in turns
                ],
                mode="lines+markers",
                name=name,
                hovertemplate=(
                    "Turno %{x}<br>Entregados %{y:.1f}%<extra>%{fullData.name}</extra>"
                ),
            )
        )

    fig.update_layout(
        title="Progreso de entregas por mapa",
        xaxis_title="Turno",
        yaxis=dict(title="Drones entregados (%)", range=[0, 105]),
        hovermode="x unified",
        template="plotly_dark",
    )
    return fig
