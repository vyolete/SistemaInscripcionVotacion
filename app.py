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
    # Credenciales desde los secretos de Streamlit
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    # Autorización con gspread
    gc = gspread.authorize(credentials)

    # Abrir la hoja usando la ID almacenada en secrets
    sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
    worksheet = sh.sheet1

    # Obtener todos los registros
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    st.stop()  # Detener la app si falla la conexión

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
    resumen_docente = df.groupby("Docente").size().reset_index(name="Cantidad de estudiantes")
    st.dataframe(resumen_docente)

    # Detalle completo
    #st.subheader("Detalle de inscripciones")
    #st.dataframe(df)
    
    # --- Resumen de equipos por docente ---
    st.subheader("Cantidad de equipos por docente")
    resumen_equipos = df.groupby("Docente")['Id_equipo'].nunique().reset_index(name="Cantidad de equipos")
    st.dataframe(resumen_equipos)

    # Filtro por docente
    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("Selecciona un docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]

    # --- Métricas principales ---
    total_estudiantes = len(df)
    total_equipos = df['Id_equipo'].nunique()
    st.metric("Total Estudiantes", total_estudiantes)
    st.metric("Total Equipos", total_equipos)

        # --- Gráfico: Equipos por docente ---
    st.subheader("📈 Equipos por Docente")
    st.bar_chart(resumen_equipos.set_index('Docente'))

    # Tabla filtrada
    #st.subheader("📋 Detalles de Inscripciones")
    #st.dataframe(df_filtrado)

    # Gráfico: Inscripciones por docente
    #st.subheader("📈 Inscripciones por Docente")
    #inscripciones_docente = df.groupby('Docente')['Id_equipo'].nunique().reset_index()
    #inscripciones_docente = inscripciones_docente.rename(columns={'Id_equipo': 'Cantidad de Equipos'})
    #st.bar_chart(inscripciones_docente.set_index('Docente'))

    # Información adicional
    st.info(
        "Cada inscripción tiene un código único que se asociará al sistema de votación. "
        "Puedes revisar los detalles de cada equipo y participante en la tabla anterior."
    )


