"""Streamlit interface for playing back a cached Fly-in simulation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import streamlit as st

from ui.interface.turn_view import TurnFigureView
from ui.visualizer.simulation_service import SimulationData, SimulationService


@dataclass
class PlaybackController:
    """Maintain the current turn and playback state across UI interactions."""

    turn: int = 0
    playing: bool = False

    def previous(self) -> None:
        """Move one turn backward, stopping at turn zero."""
        self.turn = max(0, self.turn - 1)

    def next(self, last_turn: int) -> None:
        """Move one turn forward, without passing the last turn."""
        self.turn = min(last_turn, self.turn + 1)

    def start(self, last_turn: int) -> None:
        """Start automatic playback unless the simulation has finished."""
        self.playing = self.turn < last_turn

    def pause(self) -> None:
        """Stop automatic playback on the current turn."""
        self.playing = False

    def tick(self, last_turn: int) -> None:
        """Advance one playback interval and stop at the final turn."""
        if self.playing:
            self.next(last_turn)
            if self.turn >= last_turn:
                self.pause()


class FlyInApp:
    """Coordinate map selection, Streamlit controls, and Plotly snapshots."""

    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[2]
    MAP_CATEGORIES: ClassVar[tuple[str, ...]] = (
        "easy", "medium", "hard", "challenger"
    )

    @classmethod
    def available_maps(cls) -> dict[str, str]:
        """Discover the bundled maps, grouped by difficulty and filename."""
        maps: dict[str, str] = {}
        for category in cls.MAP_CATEGORIES:
            directory = cls.ROOT / "maps" / category
            for path in sorted(directory.glob("*.txt")):
                label = (
                    f"{category.title()} / "
                    f"{path.stem.replace('_', ' ').title()}"
                )
                maps[label] = path.relative_to(cls.ROOT).as_posix()
        return maps

    def __init__(self) -> None:
        """Initialize the app without running the simulation."""
        self.simulation: SimulationData | None = None
        self.playback: PlaybackController | None = None

    @staticmethod
    @st.cache_data(show_spinner="Calculating simulation...")
    def load_simulation(path: str, map_version: int) -> SimulationData:
        """Cache a complete simulation, invalidated when the map changes."""
        # Streamlit hashes map_version even though only the path is needed.
        return SimulationService(path).build()

    def run(self) -> None:
        """Load a map and display the active playback fragment."""
        st.title("Fly-in | Drone simulation")
        maps = self.available_maps()
        if not maps:
            st.error("No map files were found in the maps directory.")
            st.stop()
            return

        map_name = st.selectbox("Select a map", list(maps))
        if map_name.startswith("Challenger / "):
            st.caption(
                "Challenger is an optional stress-test map; "
                "completion is not guaranteed."
            )
        path = self.ROOT / maps[map_name]

        try:
            map_version = path.stat().st_mtime_ns
            self.simulation = self.load_simulation(str(path), map_version)
        except (OSError, ValueError, RuntimeError) as error:
            st.error(str(error))
            st.stop()
            return

        map_key = (str(path), map_version)
        if st.session_state.get("map_key") != map_key:
            st.session_state["map_key"] = map_key
            st.session_state["playback"] = PlaybackController()

        self.playback = st.session_state["playback"]
        refresh = "850ms" if self.playback.playing else None
        st.fragment(run_every=refresh)(self.render_turn)()

    def render_turn(self) -> None:
        """Keep the plotted turn and metric counts in sync during playback."""
        simulation = self.simulation
        playback = self.playback
        if simulation is None or playback is None:
            raise RuntimeError("The simulation has not been initialized")

        last_turn = len(simulation.figure.frames) - 1
        previous, next_button, play, pause = st.columns(4)

        with previous:
            if st.button(
                "Previous",
                disabled=playback.playing or playback.turn == 0,
            ):
                playback.previous()

        with next_button:
            if st.button(
                "Next",
                disabled=playback.playing or playback.turn >= last_turn,
            ):
                playback.next(last_turn)

        with play:
            if st.button(
                "Play",
                disabled=playback.playing or playback.turn >= last_turn,
            ):
                playback.start(last_turn)
                st.rerun()

        with pause:
            if st.button("Pause", disabled=not playback.playing):
                playback.pause()
                st.rerun()

        if playback.playing:
            playback.tick(last_turn)
            if not playback.playing:
                st.rerun()

        turn = playback.turn
        counts = simulation.metrics[turn]

        st.subheader(f"Turn {turn} / {last_turn}")
        delivered, transit, waiting = st.columns(3)
        delivered.metric(
            "Delivered",
            f"{counts.delivered} / {simulation.total_drones}",
        )
        transit.metric("In transit", counts.transit)
        waiting.metric("Waiting", counts.waiting)

        viewer = TurnFigureView(simulation.figure)
        st.plotly_chart(viewer.at_turn(turn), width="stretch")


if __name__ == "__main__":
    FlyInApp().run()
