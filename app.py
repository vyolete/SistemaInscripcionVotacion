#app.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import altair as alt  # Nuevo: para gráficos bonitos

# ======================================================
# 🔹 ESTILOS PERSONALIZADOS
# ======================================================

st.markdown("""
    <style>
    /* Fondo general blanco */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Sidebar azul institucional */
    section[data-testid="stSidebar"] {
        background-color: #1B396A !important;
    }

    /* Texto en sidebar */
    .css-1d391kg, .css-q8sbsg, .css-1lcbmhc {
        color: white !important;
    }

    /* Botones personalizados */
    .stButton>button {
        background-color: #1B396A !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
        margin-bottom: 0.5em;
    }

    /* Métricas */
    .stMetric {
        background: #EEF5FB;
        border-radius: 12px;
        padding: 1em;
        margin-bottom: 1em;
        color: #1B396A;
    }
    </style>
""", unsafe_allow_html=True)


# ======================================================
# 🔹 UTILIDADES DE DATOS
# ======================================================

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

# ======================================================
# 🔹 CARGA DE DOCENTES
# ======================================================
def cargar_docentes(secrets):
    credentials = service_account.Credentials.from_service_account_info(
        secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(secrets["spreadsheet"]["id"])
    ws_docentes = sh.worksheet("Docentes")
    data = ws_docentes.get_all_records()
    return pd.DataFrame(data)

# ======================================================
# 🔹 MÓDULO INSCRIPCIÓN
# ======================================================

def modulo_inscripcion():
    st.header("📝 Formulario de Inscripción")
    st.markdown("Completa el formulario a través del siguiente módulo:")
    st.markdown(
        """
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfJaqrVwZHRbbDB8UIl4Jne9F9KMjVPMjZMM9IrD2LVWaFAwQ/viewform?embedded=true" 
        width="640" height="1177" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# 🔹 MÓDULO DASHBOARD
# ======================================================

def resumen_docente(df_filtrado):
    resumen = df_filtrado.groupby("Docente")['Cantidad de Estudiantes'].sum().reset_index()
    return resumen

def detalle_inscripciones(df_filtrado):
    st.markdown("#### Detalle de inscripciones")
    st.dataframe(df_filtrado[['Equipo', 'Docente', 'Cantidad de Estudiantes', 'ID Equipo']])

def metricas_principales(df_filtrado):
    total_inscripciones = len(df_filtrado)
    total_equipos = df_filtrado['ID Equipo'].nunique()
    total_estudiantes = df_filtrado['Cantidad de Estudiantes'].sum()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Inscripciones", total_inscripciones)
    with col2:
        st.metric("👥 Equipos", total_equipos)
    with col3:
        st.metric("🎓 Estudiantes", total_estudiantes)

def grafico_barra_docente(resumen):
    st.markdown("#### 📈 Inscripciones por Docente")
    chart = alt.Chart(resumen).mark_bar(size=35, cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
        x=alt.X('Docente:N', sort='-y', title="Docente"),
        y=alt.Y('Cantidad de Estudiantes:Q', title="Cantidad de Estudiantes"),
        color=alt.value('#1B396A'),
        tooltip=['Docente', 'Cantidad de Estudiantes']
    ).properties(height=350)
    st.altair_chart(chart, use_container_width=True)

def modulo_dashboard():
    st.header("📊 Dashboard de Inscripciones")
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
    docente_sel = st.sidebar.selectbox("Filtrar por docente", ["Todos"] + list(docentes), key="docente_select")
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)

    with st.container():
        metricas_principales(df_filtrado)
        st.markdown("---")
        resumen = resumen_docente(df_filtrado)
        grafico_barra_docente(resumen)
        with st.expander("Ver detalle de inscripciones"):
            detalle_inscripciones(df_filtrado)

    st.info(
        "Cada inscripción tiene un código único que se asociará al sistema de votación. "
        "Puedes revisar los detalles de cada equipo y participante en la tabla anterior."
    )

# ======================================================
# 🔹 MÓDULO HOME
# ======================================================
        )
def modulo_home():
    st.markdown("<h2 style='color:#1B396A; text-align:center;'>¡Bienvenido!</h2>", unsafe_allow_html=True)
    st.image("https://es.catalat.org/wp-content/uploads/2020/09/fondo-editorial-itm-2020-200x200.png", width=220)

    st.markdown("### Selecciona tu rol para comenzar:")
    rol = st.radio("Soy:", ["Estudiante", "Docente"], key="rol_radio")
    st.session_state["rol"] = rol

    if not st.session_state.get("rol_seleccionado", False):
        if st.button("Continuar"):
            st.session_state["rol_seleccionado"] = True
            st.rerun()
# ======================================================
# 🔹 MÓDULO VOTACIÓN
# ======================================================

def modulo_votacion():
    st.header("🗳 Votación de Equipos")

    params = st.query_params
    equipo_param = params.get("equipo", "")

    try:
        df_insc = conectar_google_sheets(st.secrets)
        df_insc = preparar_dataframe(df_insc)
        equipos_validos = set(df_insc["ID Equipo"].astype(str).tolist())
    except Exception as e:
        st.error(f"❌ No se pudieron cargar los equipos: {e}")
        return

    if equipo_param:
        if equipo_param in equipos_validos:
            equipo_id = equipo_param
            st.success(f"✅ Estás votando por el equipo **{equipo_id}** (detectado desde QR)")
        else:
            st.error(f"⚠️ El código de equipo «{equipo_param}» no es válido.")
            equipo_id = st.text_input("Ingresa manualmente el código del equipo a evaluar:")
    else:
        equipo_id = st.text_input("Ingresa el código del equipo a evaluar:")

    rol = st.radio("Selecciona tu rol:", ["Docente", "Estudiante/Asistente"])
    correo = st.text_input("Ingresa tu correo institucional para validar el voto:")

    if rol == "Docente":
        rigor = st.slider("Rigor técnico", 1, 5, 3)
        viabilidad = st.slider("Viabilidad financiera", 1, 5, 3)
        innovacion = st.slider("Innovación", 1, 5, 3)
        puntaje_total = rigor + viabilidad + innovacion
    else:
        creatividad = st.slider("Creatividad", 1, 5, 3)
        claridad = st.slider("Claridad de la presentación", 1, 5, 3)
        impacto = st.slider("Impacto percibido", 1, 5, 3)
        puntaje_total = creatividad + claridad + impacto

    if st.button("Enviar voto"):
        if not correo or not equipo_id:
            st.error("❌ Debes ingresar tu correo y el código de equipo")
            return

        try:
            if equipo_id not in equipos_validos:
                st.error("❌ El código de equipo no es válido")
                return

            if rol == "Docente":
                df_docentes = cargar_docentes(st.secrets)
                if correo not in df_docentes["Correo"].values:
                    st.error("❌ Tu correo no está autorizado como jurado docente.")
                    return

            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp"], scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            gc = gspread.authorize(credentials)
            sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
            ws_votos = sh.worksheet("Votaciones")

            votos = pd.DataFrame(ws_votos.get_all_records())
            if not votos.empty:
                existe = votos[(votos["Correo"] == correo) & (votos["ID Equipo"] == equipo_id)]
                if not existe.empty:
                    st.error("❌ Ya registraste un voto para este equipo")
                    return

            registro = [str(datetime.now()), rol, correo, equipo_id, puntaje_total]
            ws_votos.append_row(registro)
            st.success("✅ ¡Tu voto ha sido registrado!")

        except Exception as e:
            st.error(f"⚠️ Error al registrar el voto: {e}")

# ======================================================
# 🔹 MÓDULO RESULTADOS
# ======================================================

def modulo_resultados():
    html_warning = """
    <div style="
        text-align:center;
        font-size:1.05em;
        background:#fff8e6; 
        border-left:6px solid #1B396A;
        padding:16px; 
        border-radius:10px;
        font-family:Arial, sans-serif;
        color:#1B396A;">
      <div style="font-size:1.4em; margin-bottom:6px;">⚠️ Atención</div>
      <div>
        El sistema de votación estará disponible <b>solo durante el evento</b>.<br>
        Escanea el QR y completa tu evaluación con <b>responsabilidad</b>.
      </div>
    </div>
    """
    st.markdown(html_warning, unsafe_allow_html=True)

# ======================================================
# 🔹 MAIN APP
# ======================================================

from streamlit_option_menu import option_menu

def main():
    st.set_page_config(
        page_title="Concurso Analítica Financiera",
        page_icon="📊",
        layout="wide"
    )

    # --- Cabecera decorativa ---
    st.markdown("""
    <div style="
      height: 10px;
      margin-bottom: 15px;
      background: linear-gradient(270deg, #1B396A, #27ACE2, #1B396A, #27ACE2);
      background-size: 600% 600%;
      animation: gradientAnim 6s ease infinite;
      border-radius: 6px;">
    </div>
    <style>
    @keyframes gradientAnim {
      0% {background-position:0% 50%}
      50% {background-position:100% 50%}
      100% {background-position:0% 50%}
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h1 style='text-align: center; color: #1B396A;'>🏆 Concurso Analítica Financiera ITM</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align: center; color: #1B396A;'>¡Participa, aprende y gana!</h4>",
        unsafe_allow_html=True
    )

    # --- Inicialización de estados ---
    if "rol" not in st.session_state: 
        st.session_state.rol = None
    if "rol_seleccionado" not in st.session_state: 
        st.session_state.rol_seleccionado = False

    # --- Menú lateral ---
    with st.sidebar:
        st.image("https://es.catalat.org/wp-content/uploads/2020/09/fondo-editorial-itm-2020-200x200.png", width=140)
        st.markdown("<h3 style='color:white;'>Menú principal</h3>", unsafe_allow_html=True)

        if st.session_state.rol_seleccionado:
            if st.session_state.rol == "Docente":
                opcion = option_menu(
                    None,
                    ["Home", "Inscripción", "Dashboard", "Votación", "Resultados"],
                    icons=["house", "file-earmark-text", "bar-chart", "check2-square", "trophy"],
                    default_index=0,
                    styles={
                        "container": {"background-color": "#F3F5F7"},
                        "icon": {"color": "#1B396A", "font-size": "18px"},
                        "nav-link": {"font-size": "14px", "text-align": "left", "--hover-color": "#eee"},
                        "nav-link-selected": {"background-color": "#1B396A", "color": "white"},
                    },
                    orientation="vertical"
                )
            else:  # Estudiante
                opcion = option_menu(
                    None,
                    ["Home", "Inscripción", "Votación", "Resultados"],
                    icons=["house", "file-earmark-text", "check2-square", "trophy"],
                    default_index=0,
                    styles={
                        "container": {"background-color": "#F3F5F7"},
                        "icon": {"color": "#1B396A", "font-size": "18px"},
                        "nav-link": {"font-size": "14px", "text-align": "left", "--hover-color": "#eee"},
                        "nav-link-selected": {"background-color": "#1B396A", "color": "white"},
                    },
                    orientation="vertical"
                )
        else:
            opcion = "Home"

    # --- Router de módulos ---
    if opcion == "Home":
        modulo_home()
    elif opcion == "Inscripción":
        modulo_inscripcion()
    elif opcion == "Dashboard":
        modulo_dashboard()
    elif opcion == "Votación":
        modulo_votacion()
    elif opcion == "Resultados":
        modulo_resultados()

if __name__ == "__main__":
    main()




