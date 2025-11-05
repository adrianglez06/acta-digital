import streamlit as st
import hashlib, time, json
from pathlib import Path

st.set_page_config(page_title="Acta Digital con Hash", page_icon="📝", layout="centered")
DATA_FILE = Path("registros.jsonl")  # JSON Lines para guardar múltiples registros

st.title("Acta Digital con Hash")
st.caption("Streamlit para interfaz. hashlib para hash. time para timestamp. json para persistencia.")

# Formulario
with st.form("acta_form"):
    contenido = st.text_area("Contenido del acta", height=180, placeholder="Escribe el acta aquí")
    enviado = st.form_submit_button("Guardar")

# Guardado
if enviado:
    if not contenido.strip():
        st.error("El contenido está vacío. Escribe algo con sentido.")
    else:
        ts = int(time.time())
        payload = {"contenido": contenido, "timestamp": ts}
        # Hash determinista del payload en JSON canónico
        canon = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(canon).hexdigest()

        registro = {
            "id": digest,
            "contenido": contenido,
            "timestamp": ts
        }

        # Añade como línea JSON en un fichero .jsonl
        with DATA_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")

        st.success("Acta guardada correctamente")
        st.code(f"ID del acta (SHA-256): {digest}")

# Visualización de últimos registros
st.subheader("Últimos registros")
if DATA_FILE.exists():
    filas = DATA_FILE.read_text(encoding="utf-8").strip().splitlines()
    ultimos = [json.loads(x) for x in filas[-10:]] if filas else []
    if ultimos:
        for r in reversed(ultimos):
            st.write(f"ID: {r['id']}")
            st.write(f"Fecha Unix: {r['timestamp']}")
            st.write(r["contenido"])
            st.write("---")
    else:
        st.info("No hay registros todavía.")
else:
    st.info("Aún no se ha creado el archivo de registros.")

