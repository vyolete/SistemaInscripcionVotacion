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
    "Visualiza las inscripciones por docente, el estado de cada equipo y los participantes registrados."
)

# --- VALIDAR DATOS ---
if df.empty:
    st.warning("No hay inscripciones registradas todavía.")
else:
    # Crear columna temporal con cantidad de estudiantes por equipo
    df['Cantidad_estudiantes_equipo'] = df['Inscripción Participantes'].apply(lambda x: len([p.strip() for p in x.split(',')]))

    # Resumen por docente
    st.subheader("Resumen por docente")
    resumen_docente = df.groupby("Docente").agg(
        Cantidad_de_Equipos=("Nombre del Equipo", "nunique"),
        Cantidad_de_Estudiantes=("Cantidad_estudiantes_equipo", "sum")
    ).reset_index()
    st.dataframe(resumen_docente)
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

