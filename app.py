# app.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Dashboard Concurso Analítica Financiera",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Concurso ITM de Analítica Financiera")
st.markdown(
    "Visualiza las inscripciones por docente, el estado de cada equipo y los participantes registrados."
)

# --- CONEXIÓN CON GOOGLE SHEETS ---
# app.py
import os
import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Dashboard Concurso ITM", layout="wide")

# --- Leer variables de entorno ---
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")

if not SPREADSHEET_ID or not SERVICE_ACCOUNT_JSON:
    st.error("❌ No se encontraron las variables de entorno. Por favor configúralas en Streamlit.")
    st.stop()
import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

# Leer secrets
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]

creds_dict = json.loads(SERVICE_ACCOUNT_JSON)

# --- Especificar los scopes necesarios ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(creds)


# --- Convertir el JSON a diccionario ---
try:
    creds_dict = json.loads(SERVICE_ACCOUNT_JSON)
except json.JSONDecodeError:
    st.error("❌ Error al leer SERVICE_ACCOUNT_JSON. Revisa el formato del JSON.")
    st.stop()

# --- Autenticación con Google Sheets ---
try:
    sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
    data = sheet.get_all_records()
    st.write(data)
except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    st.stop()

# --- Leer datos ---
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📊 Dashboard Concurso ITM")

if df.empty:
    st.warning("No hay inscripciones registradas todavía.")
else:
    st.subheader("Resumen por docente")
    resumen_docente = df.groupby("Docente seleccionado").size().reset_index(name="Cantidad de inscritos")
    st.dataframe(resumen_docente)

    st.subheader("Detalle de inscripciones")
    st.dataframe(df)

# --- FILTRO POR DOCENTE ---
docentes = df['docenteSel'].unique()
docente_sel = st.sidebar.selectbox("Selecciona un docente", ["Todos"] + list(docentes))

if docente_sel != "Todos":
    df_filtrado = df[df['docenteSel'] == docente_sel]
else:
    df_filtrado = df

# --- METRICAS PRINCIPALES ---
st.metric("Total Inscripciones", len(df_filtrado))
st.metric("Total Equipos", df_filtrado['equipo'].nunique())

# --- TABLA DE INSCRIPCIONES ---
st.subheader("📋 Detalles de Inscripciones")
st.dataframe(df_filtrado)

# --- GRÁFICO: Inscripciones por docente ---
st.subheader("📈 Inscripciones por Docente")
inscripciones_docente = df.groupby('docenteSel')['equipo'].nunique().reset_index()
inscripciones_docente = inscripciones_docente.rename(columns={'equipo': 'Cantidad de Equipos'})

st.bar_chart(inscripciones_docente.set_index('docenteSel'))

# --- INFORMACION ADICIONAL ---
st.info(
    "Cada inscripción tiene un código único que se asociará al sistema de votación. "
    "Puedes revisar los detalles de cada equipo y participante en la tabla anterior."
)

