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
# Requiere que tengas un archivo de credenciales JSON de un service account
SERVICE_ACCOUNT_FILE = "credenciales.json"  # <- coloca tu archivo de credenciales
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
gc = gspread.authorize(creds)

# ID de la hoja de cálculo
SPREADSHEET_ID = "TU_ID_DE_GOOGLE_SHEET_AQUI"
SHEET_NAME = "Respuestas de formulario 1"

sheet = gc.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)
data = worksheet.get_all_records()

# --- CONVERTIR A DATAFRAME ---
df = pd.DataFrame(data)

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

