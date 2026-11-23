
import streamlit as st

st.title("Fly-in | Prueba Streamlit")

if "turno" not in st.session_state:
    st.session_state.turno = 0

st.write("Simulación de prueba: 5 turnos")

izquierda, derecha = st.columns(2)

with izquierda:
    if st.button("Anterior", disabled=st.session_state.turno == 0):
        st.session_state.turno -= 1

with derecha:
    if st.button("Siguiente", disabled=st.session_state.turno == 5):
        st.session_state.turno += 1

st.metric("Turno actual", st.session_state.turno)

st.progress(st.session_state.turno / 5)

