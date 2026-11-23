"""Explore cached Fly-in simulations turn by turn in Streamlit."""

from pathlib import Path

import streamlit as st

from ui.visualizer.simulation_service import build_simulation


ROOT = Path(__file__).resolve().parent

MAPAS = {
    "Mapa lineal": "maps/easy/01_linear_path.txt",
    "Mapa de prioridades": "maps/medium/03_priority_puzzle.txt",
}


@st.cache_data(show_spinner="Calculando simulación...")
def cargar_simulacion(path: str, version: int):
    """Cache the finished result, not the mutable simulation graph."""
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

ultimo_turno = len(figura.frames) - 1

anterior, siguiente = st.columns(2)

with anterior:
    if st.button("Anterior", disabled=st.session_state.turno == 0):
        st.session_state.turno -= 1

with siguiente:
    if st.button(
        "Siguiente",
        disabled=st.session_state.turno >= ultimo_turno,
    ):
        st.session_state.turno += 1

turno = st.session_state.turno
datos = metricas[turno]

st.subheader(f"Turno {turno} / {ultimo_turno}")

col1, col2, col3 = st.columns(3)
col1.metric("Entregados", f"{datos.delivered} / {total_drones}")
col2.metric("En tránsito", datos.transit)
col3.metric("En espera", datos.waiting)

# Update only the drone layer; the underlying map remains unchanged.
fotograma = figura.frames[turno]
figura.data[-1].update(fotograma.data[0].to_plotly_json())
figura.frames = []
figura.update_layout(
    title=f"Fly-in | Turno {turno}",
    sliders=[],
    updatemenus=[],
)

st.plotly_chart(figura, width="stretch")
