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

    /* Menú lateral */
    .nav-link {
        font-size: 15px !important;
        margin: 4px 0;
        border-radius: 6px;
    }
    .nav-link:hover {
        background-color: #27406d !important;
        color: #FFFFFF !important;
    }
    .nav-link-selected {
        background-color: #27ACE2 !important;
        color: #FFFFFF !important;
    }

    /* Botón continuar pequeño */
    .stButton>button {
        background-color: #1B396A !important;
        color: white !important;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.4em 1em;
        font-size: 13px;
    }
        /* Texto general de las opciones */
    div[role='radiogroup'] label {
        color: #1B396A !important;  /* Azul institucional */
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* Color del círculo seleccionado */
    div[role='radiogroup'] label div:first-child {
        border: 2px solid #1B396A !important;   /* Borde azul */
    }
    div[role='radiogroup'] input:checked + div:first-child {
        background-color: #1B396A !important;   /* Fondo azul cuando está seleccionado */
        border-color: #1B396A !important;
    }

    /* Texto normal */
    div[role='radiogroup'] label span {
        color: #1B396A !important;
    }
    /* Texto de la opción seleccionada */
    div[role='radiogroup'] input:checked ~ span {
        color: #27ACE2 !important;
        font-weight: 700 !important;
    }
        /* Radio buttons */
    div[role='radiogroup'] label {
        color: #1B396A !important;   /* texto normal */
        font-weight: 500 !important;
        font-size: 15px !important;
    }

    /* Círculo y texto cuando está seleccionado */
    div[role='radiogroup'] label[aria-checked="true"] {
        color: #27ACE2 !important;   /* texto azul claro */
        font-weight: 700 !important;
    }
        /* Texto normal */
    div[role='radiogroup'] label span {
        color: #1B396A !important;
        font-weight: 500 !important;
    }

    /* Círculo borde */
    div[role='radiogroup'] input[type="radio"] + div {
        border: 2px solid #1B396A !important;
    }
    
    /* Círculo seleccionado */
    div[role='radiogroup'] input[type="radio"]:checked + div {
        background-color: #1B396A !important;
        border-color: #1B396A !important;
    }
    
    /* Texto seleccionado */
    div[role='radiogroup'] input[type="radio"]:checked ~ span {
        color: #27ACE2 !important;
        font-weight: 700 !important;
    }

    
    div[role='radiogroup'] label[aria-checked="true"] svg {
        fill: #1B396A !important;    /* círculo azul */
    }

    /* Textos generales (inputs, radios, sliders) */
    .stRadio label, .stTextInput label, .stSlider label, div[role='radiogroup'] label span {
        color: #1B396A !important;
        font-weight: 500 !important;
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
    # Logo
    st.markdown(
    """
    <div style='text-align:center; position:relative; z-index:10; background-color: transparent;'>
      <img src='https://es.catalat.org/wp-content/uploads/2020/09/fondo-editorial-itm-2020-200x200.png' width='160'>
    </div>
    """,
    unsafe_allow_html=True
)


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

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📝 Inscripciones", len(df_filtrado))
    with col2: st.metric("👥 Equipos", df_filtrado['ID Equipo'].nunique())
    with col3: st.metric("🎓 Estudiantes", df_filtrado['Cantidad de Estudiantes'].sum())

    resumen = df_filtrado.groupby("Docente")['Cantidad de Estudiantes'].sum().reset_index()
    chart = alt.Chart(resumen).mark_bar(size=35, cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
        x=alt.X('Docente:N', sort='-y'),
        y=alt.Y('Cantidad de Estudiantes:Q'),
        color=alt.value('#1B396A'),
        tooltip=['Docente', 'Cantidad de Estudiantes']
    ).properties(height=350)
    st.altair_chart(chart, use_container_width=True)


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




