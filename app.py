# app.py
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
try:
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    st.stop()

# --- TÍTULO ---
st.title("📊 Dashboard Concurso ITM")
st.markdown(
    "Visualiza la cantidad de equipos y estudiantes registrados por docente, sin mostrar datos sensibles de los participantes."
)

# --- VALIDAR DATOS ---
if df.empty:
    st.warning("No hay inscripciones registradas todavía.")
else:
    # --- Renombrar columnas para uso interno ---
    df = df.rename(columns={
        "Docente": "docenteSel",
        "Nombre del Equipo": "equipo",
        "Inscripción Participantes": "participantes"
    })

    # --- Resumen por docente ---
    resumen_docente = df.groupby("docenteSel").agg(
        Cantidad_de_Equipos=("equipo", "nunique"),
        Cantidad_de_Estudiantes=("participantes", "count")
    ).reset_index()

    st.subheader("Resumen por docente")
    st.dataframe(resumen_docente)

    # --- Filtro por docente ---
    docentes = df['docenteSel'].unique()
    docente_sel = st.sidebar.selectbox("Selecciona un docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['docenteSel'] == docente_sel]

    # --- Métricas principales ---
    st.metric("Total Equipos", df_filtrado['equipo'].nunique())
    st.metric("Total Estudiantes", df_filtrado['participantes'].count())

    # --- Tabla filtrada ---
    st.subheader("📋 Equipos registrados")
    # Mostrar solo equipo y docente, sin datos sensibles
    st.dataframe(df_filtrado[["docenteSel", "equipo"]].drop_duplicates())

    # --- Gráfico ---
    st.subheader("📈 Equipos por Docente")
    inscripciones_docente = df.groupby('docenteSel')['equipo'].nunique().reset_index()
    inscripciones_docente = inscripciones_docente.rename(columns={'equipo': 'Cantidad de Equipos'})
    st.bar_chart(inscripciones_docente.set_index('docenteSel'))

    # --- Información adicional ---
    st.info(
        "Cada equipo tiene un código único asociado, pero los participantes individuales no se muestran para proteger su información."
    )

