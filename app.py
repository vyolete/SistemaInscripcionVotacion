import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import altair as alt
from streamlit_option_menu import option_menu


# ======================================================
# 🔹 ESTILOS PERSONALIZADOS
# ======================================================
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Sidebar azul */
    section[data-testid="stSidebar"] {
        background-color: #1B396A !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    /* ===== EXPANDER HEADER ===== */
    div[data-testid="stExpander"] > details > summary {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #1B396A !important;   /* Azul oscuro institucional */
        background-color: #F3F7FB !important;
        border: 1px solid #d9e1ec !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        cursor: pointer;
    }

    /* Hover */
    div[data-testid="stExpander"] > details > summary:hover {
        background-color: #E6F0FA !important;
        color: #1B396A !important;
    }

    /* ===== CONTENIDO INTERNO ===== */
    div[data-testid="stExpander"] div[data-testid="stExpanderContent"] {
        background-color: #FFFFFF !important;
        border-left: 3px solid #1B396A !important;
        padding: 12px 15px !important;
        border-radius: 0 0 6px 6px !important;
    }
    /* Títulos principales */
    div.block-container h1, 
    div.block-container h2, 
    div.block-container h3, 
    div.block-container h4, 
    div.block-container h5, 
    div.block-container h6 {
        color: #1B396A !important;
    }

    /* Botón continuar */
    .stButton>button {
        background-color: #1B396A !important;
        color: white !important;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.4em 1.2em;
        font-size: 14px;
        margin-top: 10px;
    }

    /* ===== TARJETA DE ROLES ===== */
    .rol-card {
        background-color: #F9FBFD;
        border: 1px solid #d9e1ec;
        border-radius: 12px;
        padding: 20px;
        max-width: 500px;
        margin: auto;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        text-align: center;
    }

    .rol-card h3 {
        color: #1B396A !important;
        margin-bottom: 18px;
        font-size: 18px;
        font-weight: 700;
    }

    /* ===== RADIO BUTTONS ===== */
    div[role='radiogroup'] {
        display: flex;
        justify-content: center;
        gap: 20px;
    }

    div[role='radiogroup'] label {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1B396A !important;
        cursor: pointer;
        padding: 6px 12px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    /* círculo borde */
    div[role='radiogroup'] label div:first-child {
        border: 2px solid #1B396A !important;
        border-radius: 50%;
    }

    /* opción seleccionada */
    div[role='radiogroup'] input:checked + div:first-child {
        background-color: #1B396A !important;
        border-color: #1B396A !important;
    }
    div[role='radiogroup'] input:checked + div:first-child + span {
        color: #27ACE2 !important;
        font-weight: 700 !important;
    }

    /* efecto hover */
    div[role='radiogroup'] label:hover {
        background-color: #e6f0fa;
    }

    /* Botón continuar más compacto */
    .stButton>button {
        background-color: #1B396A !important;
        color: white !important;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5em 1.2em;
        font-size: 14px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================
# 🔹 UTILIDADES
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
# 🔹 MÓDULOS
# ======================================================

def modulo_home():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(
            "https://es.catalat.org/wp-content/uploads/2020/09/fondo-editorial-itm-2020-200x200.png",
            width=180,
            unsafe_allow_html=True
        )
    # Logo


    # Títulos
    st.markdown("<h1 style='text-align:center; color:#1B396A;'>🏆 Concurso Analítica Financiera ITM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1B396A;'>¡Participa, aprende y gana!</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


    st.markdown("<h4 style='color:#1B396A; margin-bottom:15px;'>Selecciona tu rol para comenzar:</h4>", unsafe_allow_html=True)
    # CSS para cambiar color de texto del radio
    st.markdown("""
        <style>
        div[role='radiogroup'] label div:first-child {
            background-color: #1B396A !important;  /* Azul institucional */
            border-color: #1B396A !important;
        }
        </style>
    """, unsafe_allow_html=True)

    
    # Radio normal (sin background-color)
    rol = st.radio("Soy:", ["Estudiante", "Docente"], key="rol_radio", horizontal=True)
    st.session_state["rol"] = rol



    # Botón siempre visible (centrado y pequeño)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Continuar ▶️"):
            st.session_state["rol_seleccionado"] = True
            st.rerun()


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


def modulo_dashboard():
    st.header("📊 Dashboard de Inscripciones")

    # --- Cargar datos ---
    try:
        df = conectar_google_sheets(st.secrets)
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        st.stop()

    if df.empty:
        st.warning("⚠️ No hay inscripciones registradas todavía.")
        return

    # --- Preparar dataframe ---
    df = preparar_dataframe(df)
    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("📌 Filtrar por docente", ["Todos"] + list(docentes), key="docente_select")
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)

    # --- Cards de métricas ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="display:flex; align-items:center; background:#EEF5FB; 
                    padding:15px; border-radius:12px; box-shadow:0px 2px 6px rgba(0,0,0,0.1);">
            <div style="font-size:40px; margin-right:15px;">📝</div>
            <div>
                <div style="font-size:28px; font-weight:bold; color:#1B396A;">{len(df_filtrado)}</div>
                <div style="font-size:14px; color:#1B396A;">Inscripciones</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="display:flex; align-items:center; background:#EEF5FB; 
                    padding:15px; border-radius:12px; box-shadow:0px 2px 6px rgba(0,0,0,0.1);">
            <div style="font-size:40px; margin-right:15px;">👥</div>
            <div>
                <div style="font-size:28px; font-weight:bold; color:#1B396A;">{df_filtrado['ID Equipo'].nunique()}</div>
                <div style="font-size:14px; color:#1B396A;">Equipos</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="display:flex; align-items:center; background:#EEF5FB; 
                    padding:15px; border-radius:12px; box-shadow:0px 2px 6px rgba(0,0,0,0.1);">
            <div style="font-size:40px; margin-right:15px;">🎓</div>
            <div>
                <div style="font-size:28px; font-weight:bold; color:#1B396A;">{df_filtrado['Cantidad de Estudiantes'].sum()}</div>
                <div style="font-size:14px; color:#1B396A;">Estudiantes</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Gráfico ---
    resumen = df_filtrado.groupby("Docente")['Cantidad de Estudiantes'].sum().reset_index()
    st.subheader("📊 Inscripciones por Docente")
    chart = (
        alt.Chart(resumen)
        .mark_bar(size=35, cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X('Docente:N', sort='-y', title="Docente"),
            y=alt.Y('Cantidad de Estudiantes:Q', title="Estudiantes"),
            color=alt.value('#1B396A'),
            tooltip=['Docente', 'Cantidad de Estudiantes']
        )
        .properties(height=350)
    )
    st.altair_chart(chart, use_container_width=True)

    # --- Detalle opcional ---
    with st.expander("📋 Ver detalle de inscripciones", expanded=False):
        st.dataframe(df_filtrado[['Equipo', 'Docente', 'Cantidad de Estudiantes', 'ID Equipo']])


def modulo_votacion():
    st.header("🗳 Votación de Equipos")
    # (igual al tuyo) ...


def modulo_resultados():
    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:1.05em;
            background:#fff8e6; 
            border-left:6px solid #1B396A;
            padding:16px; 
            border-radius:10px;
            color:#1B396A;">
          <div style="font-size:1.4em; margin-bottom:6px;">⚠️ Atención</div>
          <div>
            El sistema de votación estará disponible <b>solo durante el evento</b>.<br>
            Escanea el QR y completa tu evaluación con <b>responsabilidad</b>.
          </div>
        </div>
        """, unsafe_allow_html=True
    )


# ======================================================
# 🔹 MAIN APP
# ======================================================
def main():
    st.set_page_config(page_title="Concurso Analítica Financiera", page_icon="📊", layout="wide")

    # Cabecera
    st.markdown("""
    <div style="height: 10px; margin-bottom: 15px;
      background: linear-gradient(270deg, #1B396A, #27ACE2, #1B396A, #27ACE2);
      background-size: 600% 600%; animation: gradientAnim 6s ease infinite;
      border-radius: 6px;"></div>
    <style>@keyframes gradientAnim {
      0% {background-position:0% 50%}
      50% {background-position:100% 50%}
      100% {background-position:0% 50%}
    }</style>
    """, unsafe_allow_html=True)

    if "rol" not in st.session_state: st.session_state.rol = None
    if "rol_seleccionado" not in st.session_state: st.session_state.rol_seleccionado = False

    # Sidebar
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
                        "container": {"background-color": "#1B396A"},
                        "icon": {"color": "white", "font-size": "18px"},
                        "nav-link": {"font-size": "15px", "color": "white", "text-align": "left"},
                        "nav-link-selected": {"background-color": "#27ACE2", "color": "white"},
                    }
                )
            else:
                opcion = option_menu(
                    None,
                    ["Home", "Inscripción", "Votación", "Resultados"],
                    icons=["house", "file-earmark-text", "check2-square", "trophy"],
                    default_index=0,
                    styles={
                        "container": {"background-color": "#1B396A"},
                        "icon": {"color": "white", "font-size": "18px"},
                        "nav-link": {"font-size": "15px", "color": "white", "text-align": "left"},
                        "nav-link-selected": {"background-color": "#27ACE2", "color": "white"},
                    }
                )
        else:
            opcion = "Home"

    # Router
    if opcion == "Home": modulo_home()
    elif opcion == "Inscripción": modulo_inscripcion()
    elif opcion == "Dashboard": modulo_dashboard()
    elif opcion == "Votación": modulo_votacion()
    elif opcion == "Resultados": modulo_resultados()


if __name__ == "__main__":
    main()




