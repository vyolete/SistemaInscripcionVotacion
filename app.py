import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Dashboard Concurso Analítica Financiera",
    page_icon="📊",
    layout="wide"
)

# --- CONEXIÓN CON GOOGLE SHEETS ---
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp"], scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

gc = gspread.authorize(credentials)
sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
worksheet = sh.sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- TÍTULO ---
st.title("📊 Dashboard Concurso ITM")
st.markdown(
    "Visualiza las inscripciones por docente, el estado de cada equipo y los participantes registrados."
)

# --- VALIDAR DATOS ---
if df.empty:
    st.warning("No hay inscripciones registradas todavía.")
else:
    # Resumen por docente
    st.subheader("Resumen por docente")
    resumen_docente = df.groupby("docenteSel").size().reset_index(name="Cantidad de inscritos")
    st.dataframe(resumen_docente)

    # Detalle completo
    st.subheader("Detalle de inscripciones")
    st.dataframe(df)

    # Filtro por docente
    docentes = df['docenteSel'].unique()
    docente_sel = st.sidebar.selectbox("Selecciona un docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['docenteSel'] == docente_sel]

    # Métricas principales
    st.metric("Total Inscripciones", len(df_filtrado))
    st.metric("Total Equipos", df_filtrado['equipo'].nunique())

    # Tabla filtrada
    st.subheader("📋 Detalles de Inscripciones")
    st.dataframe(df_filtrado)

    # Gráfico
    st.subheader("📈 Inscripciones por Docente")
    inscripciones_docente = df.groupby('docenteSel')['equipo'].nunique().reset_index()
    inscripciones_docente = inscripciones_docente.rename(columns={'equipo': 'Cantidad de Equipos'})
    st.bar_chart(inscripciones_docente.set_index('docenteSel'))

    # Información adicional
    st.info(
        "Cada inscripción tiene un código único que se asociará al sistema de votación. "
        "Puedes revisar los detalles de cada equipo y participante en la tabla anterior."
    )

