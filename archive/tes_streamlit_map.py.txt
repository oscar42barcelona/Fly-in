python3 -m streamlit run tes_streamlit_map.py
import streamlit as st

from input.receiver import receiver
from DroneGen.Graph.MapFactory import Factory
from ui.visualizer.plotly_test import plotlyzer


MAPAS = {
    "Mapa lineal": "maps/easy/01_linear_path.txt",
    "Mapa de prioridades": "maps/medium/03_priority_puzzle.txt",
}

st.title("Fly-in | Visualizador")

nombre_mapa = st.selectbox("Selecciona un mapa", list(MAPAS))
ruta = MAPAS[nombre_mapa]

modelo = receiver(ruta).Process()

if modelo is None:
    st.error("No se ha podido cargar el mapa.")
    st.stop()

grafo = Factory().create_graph(
    hubs=modelo.HUBS,
    connections=modelo.CONNECTIONS,
)

figura = plotlyzer(grafo).create_figure()

st.plotly_chart(figura, width="stretch")

col1, col2 = st.columns(2)

with col1:
    st.metric("Zonas", len(grafo.nodes))

with col2:
    st.metric("Conexiones", len(grafo.connections))

