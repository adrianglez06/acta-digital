
import streamlit as st
import hashlib, time, json

import re
import os




# -------------------------------

# Prompt 4 — Interfaz de registro (mejorada)

# -------------------------------



import os

import re



def normalize_text(s: str) -> str:

  if not s:

    return ""

  # Normaliza saltos de línea y espacios accidentales

  s = s.replace("\r\n", "\n").replace("\r", "\n")

  return s.strip()



def get_hash(text: str) -> str:

  text = normalize_text(text)

  return hashlib.sha256(text.encode("utf-8")).hexdigest()



def is_hex64(s: str) -> bool:

  return bool(re.fullmatch(r"[0-9a-fA-F]{64}", (s or "").strip()))



# Init ledger en sesión (append-only)

if "ledger" not in st.session_state:

  st.session_state["ledger"] = []  # cada item: {"owner","content_hash","time"}



st.title("🧾 Registro de Documentos Digitales")



owner  = st.text_input("Propietario")

content = st.text_area("Contenido del documento")



colA, colB = st.columns([1,1])



with colA:

  if st.button("🔐 Calcular hash"):

    if not content:

      st.warning("Escribe contenido antes de calcular el hash.")

    else:

      h = get_hash(content)

      st.session_state["hash_actual"] = h

      st.info("Hash calculado (SHA-256) del TEXTO, no del hash:")

      st.code(h, language="text")



with colB:

  if st.button("🧩 Registrar (append-only)"):

    if not owner:

      st.warning("Indica el propietario.")

    elif not content:

      st.warning("Escribe el contenido del documento.")

    else:

      h = get_hash(content)

      ts = time.time()

      record = {"owner": owner, "content_hash": h, "time": ts}



      # 1) Añadir a ledger en memoria (persistente durante la sesión)

      st.session_state["ledger"].append(record)



      # 2) Escribir en archivo local como JSON Lines (no persistente en la nube)

      #  Útil para descargar; cada línea es un registro independiente.

      try:

        with open("blockchain.jsonl", "a", encoding="utf-8") as f:

          f.write(json.dumps(record, ensure_ascii=False) + "\n")

        wrote_file = True

      except Exception as e:

        wrote_file = False

        st.warning(f"No se pudo escribir archivo local: {e}")



      st.success("Documento registrado con éxito ✅")

      st.write("**Propietario:**", owner)

      st.write("**Timestamp:**", ts, f"({time.ctime(ts)})")

      st.write("**Hash (SHA-256):**")

      st.code(h, language="text")



# ---- Tabla de registros (sesión) ----

if st.session_state["ledger"]:

  st.subheader("📚 Registros en esta sesión")

  st.dataframe(st.session_state["ledger"], use_container_width=True)



  # Descarga del ledger de sesión como JSONL (fiable en Streamlit Cloud)

  jsonl_bytes = "\n".join(json.dumps(r, ensure_ascii=False) for r in st.session_state["ledger"]).encode("utf-8")

  st.download_button(

    "⬇️ Descargar ledger (JSONL)",

    data=jsonl_bytes,

    file_name="ledger_session.jsonl",

    mime="application/json"

  )



# ---- Verificación rápida (Texto ↔ Hash) ----

st.subheader("🔍 Verificar integridad (Texto ↔ Hash)")

texto_verificar = st.text_area("Texto a verificar:")

hash_verificar = st.text_input("Hash original (64 hex):",

                value=st.session_state.get("hash_actual",""))



if st.button("Verificar texto vs hash"):

  if not texto_verificar:

    st.warning("Introduce el texto a verificar.")

  elif not is_hex64(hash_verificar):

    st.warning("Introduce un hash válido de 64 caracteres hexadecimales.")

  else:

    hash_calculado = get_hash(texto_verificar)

    st.write("Hash calculado del texto:")

    st.code(hash_calculado, language="text")

    if hash_calculado.lower() == hash_verificar.lower():

      st.success("🎯 Coincide: el texto es íntegro.")

    else:

      st.error("⚠️ No coincide: el texto fue modificado o el hash es distinto.")



st.write("Timestamp:", time.time())
st.write("Ejemplo JSON:", json.dumps({"ok": True, "msg": "listo"}))
