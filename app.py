import streamlit as st
import hashlib
import time
import json
from pathlib import Path

# Función para generar hash SHA-256 de cualquier texto
def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# Configuración inicial de la app
st.set_page_config(page_title="Acta Digital", page_icon="🧾", layout="centered")
st.title("Acta Digital — Registro con Hash")

DATA_FILE = Path("registros.jsonl")

# Formulario de entrada
st.subheader("Registrar nueva acta")
with st.form("acta_form"):
    contenido = st.text_area("Contenido del acta", height=200, placeholder="Escribe aquí el acta...")
    enviado = st.form_submit_button("Guardar acta")

if enviado:
    if not contenido.strip():
        st.error("El contenido está vacío. Escribe algo.")
    else:
        timestamp = int(time.time())
        hash_valor = get_hash(contenido)

        registro = {
            "hash": hash_valor,
            "contenido": contenido,
            "timestamp": timestamp
        }

        # Guardar el registro como línea JSON
        with DATA_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")

        st.success("Acta guardada correctamente.")
        st.write("**Hash generado (SHA-256):**")
        st.code(hash_valor)
        st.caption(f"Timestamp: {timestamp}")

# Sección para generar hash manualmente
st.divider()
st.subheader("Generador de hash independiente")
texto = st.text_input("Escribe algo para generar su hash", "")

if texto.strip():
    hash_generado = get_hash(texto)
    st.code(hash_generado)
else:
    st.info("Introduce texto para calcular su hash.")

# Visualizar los últimos registros
st.divider()
st.subheader("Últimos registros guardados")

if DATA_FILE.exists():
    lineas = DATA_FILE.read_text(encoding="utf-8").strip().splitlines()
    if lineas:
        registros = [json.loads(l) for l in lineas[-10:]]
        for r in reversed(registros):
            st.write(f"**Hash:** {r['hash']}")
            st.write(f"**Fecha UNIX:** {r['timestamp']}")
            st.write(r["contenido"])
            st.write("---")
    else:
        st.info("No hay registros todavía.")
else:
    st.info("Aún no existe el archivo de registros.")
