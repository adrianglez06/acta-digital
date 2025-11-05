import streamlit as st
import hashlib
import time
import json
from pathlib import Path
from datetime import datetime, timezone

# =========================
# Utilidades de hashing
# =========================
def canonicalize_text(text: str) -> str:
    # Normaliza saltos de línea y espacios para evitar hashes distintos por formato
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")).strip()

def get_hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def get_hash(text: str) -> str:
    return get_hash_bytes(canonicalize_text(text).encode("utf-8"))

# =========================
# Almacenamiento tipo "cadena"
# =========================
LEDGER = Path("ledger.jsonl")

def read_last_record():
    if not LEDGER.exists():
        return None
    with LEDGER.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        if size == 0:
            return None
        # Lee hacia atrás hasta encontrar el salto de línea anterior
        chunk = 4096
        data = b""
        pos = size
        while pos > 0:
            read_size = chunk if pos >= chunk else pos
            pos -= read_size
            f.seek(pos)
            data = f.read(read_size) + data
            if b"\n" in data:
                lines = data.rstrip(b"\n").split(b"\n")
                last = lines[-1]
                try:
                    return json.loads(last.decode("utf-8"))
                except Exception:
                    return None
        # Si solo hay una línea sin \n final
        try:
            return json.loads(data.decode("utf-8"))
        except Exception:
            return None

def append_record(record: dict):
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def verify_ledger():
    if not LEDGER.exists():
        return True, 0, None
    ok = True
    count = 0
    prev_id = None
    bad_msg = None
    with LEDGER.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                ok = False
                bad_msg = f"Línea {i}: JSON inválido"
                break
            # Recalcular id esperado
            payload = {
                "owner": rec.get("owner", ""),
                "content": canonicalize_text(rec.get("content", "")),
                "time": rec.get("time"),
                "prev_id": rec.get("prev_id"),
            }
            expected_id = get_hash_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
            if rec.get("id") != expected_id:
                ok = False
                bad_msg = f"Línea {i}: id no coincide con el contenido"
                break
            if rec.get("prev_id") != prev_id:
                ok = False
                bad_msg = f"Línea {i}: prev_id no encadena con el registro anterior"
                break
            prev_id = rec.get("id")
            count += 1
    return ok, count, bad_msg

# =========================
# App Streamlit
# =========================
st.set_page_config(page_title="Registro de Documentos Digitales", layout="centered")
st.title("Registro de Documentos Digitales")

# Verificación de integridad
ok, total, error_msg = verify_ledger()
st.caption(f"Estado del ledger: {'OK' if ok else 'CORRUPTO'} | Registros: {total}")
if not ok:
    st.error(error_msg)

# Formulario de alta
st.subheader("Nuevo registro")
owner = st.text_input("Propietario")
content = st.text_area("Contenido del documento", height=200, placeholder="Pega el contenido exacto que quieres anclar")
if st.button("Registrar", type="primary"):
    if not owner.strip():
        st.error("Propietario vacío. Rellénalo.")
    elif not content.strip():
        st.error("Contenido vacío. Rellénalo.")
    else:
        ts = time.time()
        iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        norm_content = canonicalize_text(content)
        # Encadenado: cada registro referencia el id anterior
        last = read_last_record()
        prev_id = last["id"] if last else None
        payload = {
            "owner": owner.strip(),
            "content": norm_content,
            "time": ts,
            "prev_id": prev_id,
        }
        rec_id = get_hash_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        record = {
            "id": rec_id,
            "owner": payload["owner"],
            "content": payload["content"],
            "time": ts,
            "time_iso": iso,
            "prev_id": prev_id,
            "algo": "sha256",
        }
        append_record(record)
        st.success("Documento registrado con éxito")
        st.write("ID del registro")
        st.code(rec_id)
        st.write("Prueba independiente del contenido")
        st.code(get_hash(content))

st.divider()

# Generador de hash simple
st.subheader("Generar hash de un texto")
sample = st.text_input("Texto a hashear", "")
if sample.strip():
    st.code(get_hash(sample))

st.divider()

# Últimos registros
st.subheader("Últimos registros")
if LEDGER.exists() and LEDGER.stat().st_size > 0:
    with LEDGER.open("r", encoding="utf-8") as f:
        lines = [json.loads(x) for x in f if x.strip()]
    if lines:
        for rec in lines[-10:][::-1]:
            st.write(f"ID: {rec['id']}")
            st.write(f"Propietario: {rec['owner']}")
            st.write(f"Fecha (UTC): {rec['time_iso']}")
            st.write("Contenido:")
            st.code(rec["content"])
            st.caption(f"prev_id: {rec['prev_id']}")
            st.write("---")
    else:
        st.info("No hay registros.")
else:
    st.info("Aún no existe el ledger.")

# Descarga del ledger
if LEDGER.exists():
    st.download_button(
        label="Descargar ledger.jsonl",
        data=LEDGER.read_bytes(),
        file_name="ledger.jsonl",
        mime="application/json",
    )

