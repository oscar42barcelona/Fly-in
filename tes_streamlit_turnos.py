
from pathlib import Path

import streamlit as st

from input.receiver import receiver
from input.validator import HubType
from DroneGen.Graph.MapFactory import Factory
from DroneGen.Flygorithm.Algorithm import Algorithm
from DroneGen.Orchestrator import orchestrator
from ui.visualizer.plotly_test import plotlyzer


RAIZ = Path(__file__).resolve().parent

MAPAS = {
    "Mapa lineal": "maps/easy/01_linear_path.txt",
    "Mapa de prioridades": "maps/medium/03_priority_puzzle.txt",
}


# CÁLCULO: separado de los controles de la interfaz.
@st.cache_data(show_spinner="Calculando simulación...")
def calcular_simulacion(ruta: str, version_archivo: int):
    print(f"Calculando simulación: {ruta}")

    modelo = receiver(ruta).Process()

    if modelo is None:
        raise ValueError("No se ha podido cargar el mapa")

    factory = Factory()

    grafo = factory.create_graph(
        modelo.HUBS,
        modelo.CONNECTIONS,
    )

    inicio = next(
        (n for n in grafo.nodes if n.type == HubType.ENTRY),
        None,
    )

    if inicio is None:
        raise ValueError("No existe un nodo de entrada")

    drones = factory.create_drones(modelo.NB_DRONES, inicio)

    rutas = Algorithm().solve(drones[0], grafo, modelo.NB_DRONES)
    movimientos = orchestrator().plan(drones, rutas, grafo)

    figura = plotlyzer(grafo).create_visualization(movimientos)

    return figura, len(drones)


# INTERFAZ: únicamente controla qué resultado se muestra.
st.title("Fly-in | Simulación de drones")

nombre_mapa = st.selectbox(
    "Selecciona un mapa",
    list(MAPAS),
)

if st.session_state.get("mapa_cargado") != nombre_mapa:
    st.session_state.mapa_cargado = nombre_mapa
    st.session_state.turno = 0

ruta = RAIZ / MAPAS[nombre_mapa]

try:
    figura, total_drones = calcular_simulacion(
        str(ruta),
        ruta.stat().st_mtime_ns,
    )
except (OSError, ValueError, RuntimeError) as error:
    st.error(str(error))
    st.stop()

ultimo_turno = len(figura.frames) - 1

anterior, siguiente = st.columns(2)

with anterior:
    if st.button(
        "Anterior",
        disabled=st.session_state.turno == 0,
    ):
        st.session_state.turno -= 1

with siguiente:
    if st.button(
        "Siguiente",
        disabled=st.session_state.turno == ultimo_turno,
    ):
        st.session_state.turno += 1

turno = st.session_state.turno

col1, col2 = st.columns(2)
col1.metric("Turno", f"{turno} / {ultimo_turno}")
col2.metric("Drones", total_drones)

fotograma = figura.frames[turno]
figura.data[-1].update(fotograma.data[0].to_plotly_json())

figura.frames = []
figura.update_layout(
    title=f"Fly-in | Turno {turno}",
    sliders=[],
    updatemenus=[],
)

st.plotly_chart(figura, width="stretch")

