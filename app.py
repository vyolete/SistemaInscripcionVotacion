import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# ---------- UTILIDADES DE DATOS ----------
def cargar_datos_google_sheets(secrets):
    credentials = service_account.Credentials.from_service_account_info(
        secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(secrets["spreadsheet"]["id"])
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def contar_estudiantes(participantes_str):
    if not participantes_str:
        return 0
    partes = [p.strip() for p in participantes_str.split(',') if p.strip()]
    estudiantes_validos = [p for p in partes if '@' in p]
    return len(estudiantes_validos)

def preparar_dataframe(df):
    df['Cantidad_estudiantes_equipo'] = df['Inscripción Participantes'].apply(contar_estudiantes)
    return df

# ---------- UI: INSCRIPCIÓN ----------
def pestaña_inscripcion():
    st.header("Formulario de Inscripción")
    st.markdown("Completa el formulario a través del siguiente enlace:")
    st.markdown(
        """
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfJaqrVwZHRbbDB8UIl4Jne9F9KMjVPMjZMM9IrD2LVWaFAwQ/viewform?embedded=true" width="640" height="1177" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
        """,
        unsafe_allow_html=True
    )

# ---------- UI: DASHBOARD ----------
def mostrar_resumen_docente(df):
    st.subheader("Resumen por docente")
    resumen_docente = df.groupby("Docente").agg(
        Cantidad_de_Equipos=("Nombre del Equipo", "nunique"),
        Cantidad_de_Estudiantes=("Cantidad_estudiantes_equipo", "sum")
    ).reset_index()
    st.dataframe(resumen_docente)

def mostrar_metricas(df, df_filtrado):
    st.metric("Total Inscripciones", len(df_filtrado))
    st.metric("Total Estudiantes", df_filtrado['Cantidad_estudiantes_equipo'].sum())

def mostrar_tabla_filtrada(df_filtrado):
    st.subheader("📋 Detalles de Inscripciones")
    st.dataframe(df_filtrado)

def mostrar_grafico_docentes(df):
    st.subheader("📈 Inscripciones por Docente")
    inscripciones_docente = df.groupby('Docente')['Id_equipo'].nunique().reset_index()
    inscripciones_docente = inscripciones_docente.rename(columns={'Id_equipo': 'Cantidad de Equipos'})
    st.bar_chart(inscripciones_docente.set_index('Docente'))

def pestaña_dashboard(df):
    st.header("Dashboard de Inscripciones")
    st.title("📊 Dashboard Concurso ITM")
    st.markdown("Visualiza las inscripciones por docente, el estado de cada equipo y los participantes registrados.")

    if df.empty:
        st.warning("No hay inscripciones registradas todavía.")
        return

    df = preparar_dataframe(df)
    mostrar_resumen_docente(df)

    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("Selecciona un docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]

    mostrar_metricas(df, df_filtrado)
    mostrar_tabla_filtrada(df_filtrado)
    mostrar_grafico_docentes(df)
    st.info(
        "Cada inscripción tiene un código único que se asociará al sistema de votación. "
        "Puedes revisar los detalles de cada equipo y participante en la tabla anterior."
    )

# ---------- MAIN ----------
def main():
    st.set_page_config(
        page_title="Dashboard Concurso Analítica Financiera",
        page_icon="📊",
        layout="wide"
    )
    tab1, tab2 = st.tabs(["📝 Inscripción", "📊 Dashboard"])
    with tab1:
        pestaña_inscripcion()
    with tab2:
        try:
            df = cargar_datos_google_sheets(st.secrets)
        except Exception as e:
            st.error(f"❌ Error al conectar con Google Sheets: {e}")
            st.stop()
        pestaña_dashboard(df)

if __name__ == "__main__":
    main()

