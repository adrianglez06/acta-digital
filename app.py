import streamlit as st
import hashlib

def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

st.set_page_config(page_title="Acta Digital — Hash Generator", layout="centered")
st.title("Generador de hash SHA-256")

texto = st.text_input("Escribe algo para generar su hash", "")

if texto.strip():
    hash_resultado = get_hash(texto)
    st.success("Hash generado correctamente:")
    st.code(hash_resultado)
else:
    st.info("Introduce texto para calcular el hash.")


st.write("Timestamp:", time.time())
st.write("Ejemplo JSON:", json.dumps({"ok": True, "msg": "listo"}))

