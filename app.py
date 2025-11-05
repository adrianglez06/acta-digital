import streamlit as st
import hashlib, time, json


st.title("Acta Digital — Import Test")

st.write("✅ Librerías importadas:")
st.code("streamlit, hashlib, time, json")



# Función requerida
def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

st.set_page_config(page_title="Acta Digital — Hash", layout="centered")
st.title("Generador de hash SHA-256")

st.caption("Escribe algo y verás su hash en tiempo real.")

# Entrada de texto
texto = st.text_input("Texto a hashear", "hola mundo")

# Salida
if texto.strip():
    h = get_hash(texto)
    st.subheader("Hash")
    st.code(h)
    st.write(f"Longitud: {len(h)} caracteres hexadecimales")
else:
    st.info("Escribe texto para calcular el hash.")



st.write("Timestamp:", time.time())
st.write("Ejemplo JSON:", json.dumps({"ok": True, "msg": "listo"}))

