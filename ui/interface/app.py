"""Explore cached Fly-in simulations with synchronized Streamlit playback."""

from pathlib import Path

import streamlit as st

from ui.interface.turn_view import figure_at_turn
from ui.visualizer.simulation_service import build_simulation


ROOT = Path(__file__).resolve().parents[2]

MAPAS = {
    "Mapa lineal": "maps/easy/01_linear_path.txt",
    "Mapa de prioridades": "maps/medium/03_priority_puzzle.txt",
}


@st.cache_data(show_spinner="Calculando simulación...")
def cargar_simulacion(path: str, version: int):
    """Cache the simulation, not each individual playback tick."""
    return build_simulation(path)


st.title("Fly-in | Simulación de drones")

nombre_mapa = st.selectbox("Selecciona un mapa", list(MAPAS))
ruta = ROOT / MAPAS[nombre_mapa]

try:
    version = ruta.stat().st_mtime_ns
    figura, metricas, total_drones = cargar_simulacion(str(ruta), version)
except (OSError, ValueError, RuntimeError) as error:
    st.error(str(error))
    st.stop()

# Changing the map (or modifying its contents) restarts playback at turn zero.
mapa_actual = (str(ruta), version)
if st.session_state.get("mapa_actual") != mapa_actual:
    st.session_state.mapa_actual = mapa_actual
    st.session_state.turno = 0
    st.session_state.playing = False

if "playing" not in st.session_state:
    st.session_state.playing = False

ultimo_turno = len(figura.frames) - 1


@st.fragment(run_every="850ms" if st.session_state.playing else None)
def mostrar_turno() -> None:
    """Keep the plotted turn and its metrics synchronized during playback."""
    anterior, siguiente, play, pause = st.columns(4)

    with anterior:
        if st.button(
            "Anterior",
            disabled=st.session_state.playing or st.session_state.turno == 0,
        ):
            st.session_state.turno -= 1

    with siguiente:
        if st.button(
            "Siguiente",
            disabled=(
                st.session_state.playing
                or st.session_state.turno >= ultimo_turno
            ),
        ):
            st.session_state.turno += 1

    with play:
        if st.button(
            "Play",
            disabled=(
                st.session_state.playing
                or st.session_state.turno >= ultimo_turno
            ),
        ):
            st.session_state.playing = True
            st.rerun()  # Rebuild the fragment with automatic refresh enabled.

    with pause:
        if st.button("Pause", disabled=not st.session_state.playing):
            st.session_state.playing = False
            st.rerun()  # Stop the fragment's automatic refresh schedule.

    if st.session_state.playing:
        st.session_state.turno += 1
        if st.session_state.turno >= ultimo_turno:
            st.session_state.playing = False
            st.rerun()  # Rebuild without a timer at the final turn.

    turno = st.session_state.turno
    datos = metricas[turno]

    st.subheader(f"Turno {turno} / {ultimo_turno}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Entregados", f"{datos.delivered} / {total_drones}")
    col2.metric("En tránsito", datos.transit)
    col3.metric("En espera", datos.waiting)

    # A copied static frame avoids stale Plotly buttons and keeps cached
    # simulation frames available for the next Streamlit rerun.
    st.plotly_chart(figure_at_turn(figura, turno), width="stretch")


mostrar_turno()
