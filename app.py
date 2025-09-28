import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from streamlit_carousel import carousel

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
    st.markdown("Completa el formulario a través del siguiente módulo:")
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
    try:
        df = conectar_google_sheets(st.secrets)
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        st.stop()
    if df.empty:
        st.warning("No hay inscripciones registradas todavía.")
        return
    df = preparar_dataframe(df)
    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("Filtrar por docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)
    resumen = resumen_docente(df_filtrado)
    detalle_inscripciones(df_filtrado)
    metricas_principales(df_filtrado)
    grafico_barra_docente(resumen)
    st.info(
        "Cada inscripción tiene un código único que se asociará al sistema de votación. "
        "Puedes revisar los detalles de cada equipo y participante en la tabla anterior."
    )

# --- UI: HOME ---
def modulo_home():
    col1, col2 = st.columns([1,2])

    with col1:
        st.markdown("<h2 style='color:#1B396A'>¡Bienvenido!</h2>", unsafe_allow_html=True)
        st.write("Selecciona tu rol para comenzar:")
        rol = st.radio("Soy:", ["Estudiante", "Docente"], key="rol_radio")
        st.session_state["rol"] = rol
        if not st.session_state.get("rol_seleccionado", False):
            if st.button("Continuar"):
                st.session_state["rol_seleccionado"] = True
                st.rerun()

    with col2:
    # Muestra el GIF animado en vez del video
        st.image(
            "https://media4.giphy.com/media/ZBoap6UCvOEeQNGzHK/200.webp",
            caption="¡Bienvenido!",
            use_container_width=True
        )
# --- MODULOS DE VOTACION Y RESULTADOS ---
def modulo_votacion():
    html_warning = """
    <div style="text-align:center; font-size:1.05em;
                background:#fff3cd; border-left:6px solid #ffeeba;
                padding:12px; border-radius:6px;">
      <strong>⚠️ Atención:</strong><br>
      El sistema de votación está habilitado <b>solo durante el evento</b>.<br>
      Por favor, escanee el QR y complete la evaluación con responsabilidad.
    </div>
    """
    st.markdown(html_warning, unsafe_allow_html=True)

    # ... resto del código del módulo (inputs, QR, lógica de votación, etc.)


def modulo_resultados():
    html_warning = """
    <div style="
        text-align:center;
        font-size:1.05em;
        background:#fff8e6; 
        border-left:6px solid #ffb84d;
        padding:16px; 
        border-radius:10px;
        font-family:Arial, sans-serif;
        color:#5a4a00;">
      <div style="font-size:1.4em; margin-bottom:6px;">⚠️ Atención</div>
      <div>
        El sistema de votación estará disponible <b>solo durante el evento</b>.<br>
        Escanea el QR y completa tu evaluación con <b>responsabilidad</b>.
      </div>
    </div>
    """
    st.markdown(html_warning, unsafe_allow_html=True)


# --- MAIN ---
def main():
    st.set_page_config(
        page_title="Concurso Analítica Financiera",
        page_icon="📊",
        layout="wide"
    )
    # Banner superior animado
    st.markdown("""
    <div style="
      height: 12px;
      margin-bottom: 20px;
      background: linear-gradient(270deg, #1B396A, #27ACE2, #1B396A, #27ACE2);
      background-size: 600% 600%;
      animation: gradientAnim 6s ease infinite;
      border-radius: 8px;
    ">
    </div>
    <style>
    @keyframes gradientAnim {
      0% {background-position:0% 50%}
      50% {background-position:100% 50%}
      100% {background-position:0% 50%}
    }
    </style>
    """, unsafe_allow_html=True)
    # Logo ITM centrado
    st.markdown(
        f'<div style="display:flex;justify-content:center;margin-bottom:8px">'
        f'<img src="data:image/jpeg;base64,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" width="160" style="border-radius:10px;border:1px solid #ccc" /></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "<h1 style='text-align: center; color: #1B396A; font-family:sans-serif; font-weight:700; margin-bottom:0;'>🏆 Concurso Analítica Financiera ITM</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align: center; color: #27ACE2; font-family:sans-serif; margin-top:0;'>¡Participa, aprende y gana!</h4>",
        unsafe_allow_html=True
    )

    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 'Home'
    if 'rol' not in st.session_state:
        st.session_state.rol = None
    if 'rol_seleccionado' not in st.session_state:
        st.session_state.rol_seleccionado = False

    if st.session_state.active_tab == 'Home':
        modulo_home()
        if not st.session_state.rol_seleccionado or st.session_state.rol is None:
            st.warning("Por favor selecciona tu rol y presiona 'Continuar' para acceder al menú.")
            return

    with st.sidebar:
        st.header("Menú")
        if st.button("🏠 Home"):
            st.session_state.active_tab = 'Home'
            st.session_state.rol_seleccionado = False
        if st.session_state.rol_seleccionado:
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

    allowed_tabs = []
    if st.session_state.rol == "Docente":
        allowed_tabs = ['Inscripción', 'Dashboard', 'Votación', 'Resultados', 'Home']
    elif st.session_state.rol == "Estudiante":
        allowed_tabs = ['Inscripción', 'Votación', 'Resultados', 'Home']
    else:
        allowed_tabs = ['Home']

    if st.session_state.active_tab not in allowed_tabs:
        st.session_state.active_tab = 'Home'

    if st.session_state.active_tab == 'Inscripción':
        modulo_inscripcion()
    elif st.session_state.active_tab == 'Dashboard':
        modulo_dashboard()
    elif st.session_state.active_tab == 'Votación':
        modulo_votacion()
    elif st.session_state.active_tab == 'Resultados':
        modulo_resultados()
    elif st.session_state.active_tab == 'Home' and st.session_state.rol_seleccionado and st.session_state.rol is not None:
        st.info("Usa el menú lateral para navegar entre los módulos.")

if __name__ == "__main__":
    main()
