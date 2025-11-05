import streamlit as st

st.set_page_config(page_title="Acta Digital", page_icon="📝", layout="centered")

st.title("Acta Digital")
st.subheader("Registro simple de decisiones")

with st.form("acta_form"):
    tema = st.text_input("Tema")
    asistentes = st.text_area("Asistentes (una persona por línea)")
    acuerdos = st.text_area("Acuerdos")
    acciones = st.text_area("Acciones y responsables")
    enviado = st.form_submit_button("Guardar acta")

if enviado:
    st.success("Acta registrada correctamente.")
    st.write("### Resumen del acta")
    st.write(f"**Tema:** {tema}")
    st.write("**Asistentes:**")
    st.write([a.strip() for a in asistentes.splitlines() if a.strip()])
    st.write("**Acuerdos:**")
    st.write(acuerdos)
    st.write("**Acciones y responsables:**")
    st.write(acciones)
