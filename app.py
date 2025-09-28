import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# --- UTILIDADES DE DATOS ---
def conectar_google_sheets(secrets):
    credentials = service_account.Credentials.from_service_account_info(
        secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(secrets["spreadsheet"]["id"])
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def contar_participantes(participantes_str):
    if not participantes_str:
        return 0
    estudiantes = [p.strip() for p in participantes_str.split(',') if p.strip()]
    return len(estudiantes)

def preparar_dataframe(df):
    df = df.rename(columns={
        "Nombre del Equipo": "Equipo",
        "Inscripción Participantes": "Participantes",
        "Docente": "Docente",
        "Id_equipo": "ID Equipo"
    })
    return df

# --- UI: INSCRIPCIÓN ---
def modulo_inscripcion():
    st.header("Formulario de Inscripción")
    st.markdown(
        "Completa el formulario a través del siguiente módulo:"
    )
    st.markdown(
        """
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfJaqrVwZHRbbDB8UIl4Jne9F9KMjVPMjZMM9IrD2LVWaFAwQ/viewform?embedded=true" width="640" height="1177" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
        """,
        unsafe_allow_html=True
    )

# --- UI: DASHBOARD ---
def resumen_docente(df_filtrado):
    resumen = df_filtrado.groupby("Docente")['Cantidad de Estudiantes'].sum().reset_index()
    st.subheader("Resumen por docente")
    st.dataframe(resumen)
    return resumen

def detalle_inscripciones(df_filtrado):
    st.subheader("Detalle de inscripciones")
    st.dataframe(df_filtrado[['Equipo', 'Docente', 'Cantidad de Estudiantes', 'ID Equipo']])

def metricas_principales(df_filtrado):
    st.metric("Total Inscripciones", len(df_filtrado))
    st.metric("Total Equipos", df_filtrado['ID Equipo'].nunique())
    st.metric("Total Estudiantes", df_filtrado['Cantidad de Estudiantes'].sum())

def grafico_barra_docente(resumen):
    st.subheader("📈 Inscripciones por Docente")
    st.bar_chart(resumen.set_index('Docente'))

def modulo_dashboard():
    st.header("Dashboard de Inscripciones")
    # --- CONEXIÓN CON GOOGLE SHEETS ---
    try:
        df = conectar_google_sheets(st.secrets)
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        st.stop()

    # --- VALIDAR DATOS ---
    if df.empty:
        st.warning("No hay inscripciones registradas todavía.")
        return

    # --- LIMPIEZA Y RENOMBRE DE COLUMNAS ---
    df = preparar_dataframe(df)

    # --- FILTRO POR DOCENTE ---
    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("Filtrar por docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]

    # --- CÁLCULO DE PARTICIPANTES ---
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)

    # --- RESUMEN POR DOCENTE ---
    resumen = resumen_docente(df_filtrado)

    # --- DETALLE COMPLETO ---
    detalle_inscripciones(df_filtrado)

    # --- MÉTRICAS PRINCIPALES ---
    metricas_principales(df_filtrado)

    # --- GRÁFICO DE BARRAS ---
    grafico_barra_docente(resumen)

    # --- INFORMACIÓN ADICIONAL ---
    st.info(
        "Cada inscripción tiene un código único que se asociará al sistema de votación. "
        "Puedes revisar los detalles de cada equipo y participante en la tabla anterior."
    )

# --- UI: HOME ---
def modulo_home():
    st.header("Bienvenido al Concurso Analítica Financiera ITM")
    st.write("Por favor, selecciona tu rol para continuar:")
    rol = st.radio("Soy:", ["Estudiante", "Docente"], key="rol_radio")
    st.session_state["rol"] = rol

# --- MODULOS DE VOTACION Y RESULTADOS ---
def modulo_votacion():
    st.header("Módulo de Votación")
    st.info("Aquí irá el sistema de votación (por implementar).")

def modulo_resultados():
    st.header("Resultados")
    st.info("Aquí se mostrarán los resultados (por implementar).")

# --- MAIN ---
def main():
    st.set_page_config(
        page_title="Concurso Analítica Financiera",
        page_icon="📊",
        layout="wide"
    )

    st.title("🏆 Concurso Analítica Financiera ITM")

    # --- INICIALIZACIÓN DE SESSION_STATE ---
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 'Home'
    if 'rol' not in st.session_state:
        st.session_state.rol = None

    # --- MENÚ LATERAL DINÁMICO ---
    with st.sidebar:
        st.header("Menú")
        if st.button("🏠 Home"):
            st.session_state.active_tab = 'Home'
        # Menú según rol
        if st.session_state.rol == "Docente":
            if st.button("📝 Inscripción"):
                st.session_state.active_tab = 'Inscripción'
            if st.button("📊 Dashboard"):
                st.session_state.active_tab = 'Dashboard'
            if st.button("🗳 Votación"):
                st.session_state.active_tab = 'Votación'
            if st.button("📈 Resultados"):
                st.session_state.active_tab = 'Resultados'
        elif st.session_state.rol == "Estudiante":
            if st.button("📝 Inscripción"):
                st.session_state.active_tab = 'Inscripción'
            if st.button("🗳 Votación"):
                st.session_state.active_tab = 'Votación'
            if st.button("📈 Resultados"):
                st.session_state.active_tab = 'Resultados'

    # --- PROTECCIÓN DE ACCESO SEGÚN ROL ---
    allowed_tabs = []
    if st.session_state.rol == "Docente":
        allowed_tabs = ['Inscripción', 'Dashboard', 'Votación', 'Resultados', 'Home']
    elif st.session_state.rol == "Estudiante":
        allowed_tabs = ['Inscripción', 'Votación', 'Resultados', 'Home']
    else:
        allowed_tabs = ['Home']

    # Si el usuario intenta acceder a una pestaña no permitida, redirige a Home
    if st.session_state.active_tab not in allowed_tabs:
        st.session_state.active_tab = 'Home'

    # --- MOSTRAR MODULO ACTIVO ---
    if st.session_state.active_tab == 'Home':
        modulo_home()
        if st.session_state.rol is None:
            st.warning("Por favor selecciona tu rol para continuar.")
            return
    elif st.session_state.active_tab == 'Inscripción':
        modulo_inscripcion()
    elif st.session_state.active_tab == 'Dashboard':
        modulo_dashboard()
    elif st.session_state.active_tab == 'Votación':
        modulo_votacion()
    elif st.session_state.active_tab == 'Resultados':
        modulo_resultados()

if __name__ == "__main__":
    main()
