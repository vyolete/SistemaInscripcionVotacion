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
        font-family: 'Segoe UI', sans-serif;
    }

    /* Sidebar azul */
    section[data-testid="stSidebar"] {
        background-color: #1B396A !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Botones visibles */
    .stButton>button, button, .stButton>button span {
        background-color: #1B396A !important;
        color: white !important;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5em 1.2em;
        font-size: 14px;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #27406d !important;
    }
        /* Forzar color visible en botones y su texto interno */
    .stButton>button * {
        color: white !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* Títulos */
    h1, h2, h3, h4, h5, h6, label, p, span, div {
        color: #1B396A !important;
    }

    /* Expander personalizado */
    div[data-testid="stExpander"] > details > summary {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #1B396A !important;
        background-color: #F3F7FB !important;
        border: 1px solid #d9e1ec !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        cursor: pointer;
    }
    div[data-testid="stExpander"] > details > summary:hover {
        background-color: #E6F0FA !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderContent"] {
        background-color: #FFFFFF !important;
        border-left: 3px solid #1B396A !important;
        padding: 12px 15px !important;
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
            "https://upload.wikimedia.org/wikipedia/commons/7/77/ITM_logo.png",
            width=180
        )

    st.markdown("<h1 style='text-align:center;'>🏆 Concurso Analítica Financiera ITM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>¡Participa, aprende y gana!</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h4 style='text-align:center;'>Selecciona tu rol para comenzar:</h4>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎓 Soy Estudiante", use_container_width=True):
            st.session_state["rol"] = "Estudiante"
            st.session_state["rol_seleccionado"] = True
            st.rerun()

    with col2:
        if st.button("👨‍🏫 Soy Docente", use_container_width=True):
            st.session_state["rol"] = "Docente"
            st.session_state["rol_seleccionado"] = False
            st.session_state["validando_docente"] = True
            st.rerun()

    if st.session_state.get("validando_docente", False):
        correo = st.text_input("📧 Ingresa tu correo institucional para validar:")
        if st.button("Validar"):
            df_docentes = cargar_docentes(st.secrets)
            if correo in df_docentes["Correo"].values:
                st.session_state["rol_seleccionado"] = True
                st.session_state["rol"] = "Docente"
                st.session_state["validando_docente"] = False
                st.success("✅ Acceso autorizado. Bienvenido docente.")
                st.rerun()
            else:
                st.error("❌ Tu correo no está autorizado como docente.")
                if st.button("Volver al inicio"):
                    st.session_state.clear()
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
        st.warning("⚠️ No hay inscripciones registradas todavía.")
        return

    df = preparar_dataframe(df)
    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("📌 Filtrar por docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Inscripciones", len(df_filtrado))
    with col2:
        st.metric("👥 Equipos", df_filtrado['ID Equipo'].nunique())
    with col3:
        st.metric("🎓 Estudiantes", df_filtrado['Cantidad de Estudiantes'].sum())

    st.subheader("📈 Inscripciones por Docente")
    resumen = df_filtrado.groupby("Docente")['Cantidad de Estudiantes'].sum().reset_index()
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
    with st.expander("📋 Ver detalle de inscripciones", expanded=False):
        st.dataframe(df_filtrado[['Equipo', 'Docente', 'Cantidad de Estudiantes', 'ID Equipo']])


def modulo_votacion():
    st.header("🗳 Votación de Equipos")

    params = st.query_params
    equipo_qr = params.get("equipo", [None])[0] if "equipo" in params else None
    rol_qr = params.get("rol", [None])[0] if "rol" in params else None

    if equipo_qr:
        st.info(f"📲 Ingreso directo: estás votando por el equipo **{equipo_qr}**")

    if "validado_voto" not in st.session_state:
        st.session_state.validado_voto = False

    if not st.session_state.validado_voto:
        rol = "Docente" if rol_qr == "docente" else "Estudiante / Asistente" if rol_qr else st.radio(
            "Selecciona tu rol:", ["Estudiante / Asistente", "Docente"], horizontal=True
        )

        correo = st.text_input("📧 Correo institucional:")
        equipo_id = st.text_input("🏷️ Código del equipo a evaluar:", value=equipo_qr or "")

        if st.button("Continuar ▶️"):
            if not correo or not equipo_id:
                st.error("❌ Debes ingresar tu correo y el código del equipo.")
                return
            try:
                df_insc = preparar_dataframe(conectar_google_sheets(st.secrets))
                if equipo_id not in df_insc["ID Equipo"].astype(str).tolist():
                    st.error("❌ El código del equipo no existe.")
                    return
                if "Docente" in rol:
                    df_docentes = cargar_docentes(st.secrets)
                    if correo not in df_docentes["Correo"].values:
                        st.error("❌ Tu correo no está autorizado como jurado docente.")
                        return
                st.session_state.validado_voto = True
                st.session_state.rol_voto = rol
                st.session_state.correo_voto = correo
                st.session_state.equipo_voto = equipo_id
                st.success("✅ Validación exitosa. Puedes realizar la votación.")
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ Error al validar: {e}")
    else:
        rol = st.session_state.rol_voto
        correo = st.session_state.correo_voto
        equipo_id = st.session_state.equipo_voto
        st.markdown(f"<h4>📋 Evaluación del Proyecto ({rol})</h4>", unsafe_allow_html=True)

        if "Docente" in rol:
            col1, col2, col3 = st.columns(3)
            with col1: rigor = st.slider("Rigor técnico", 1, 5, 3)
            with col2: viabilidad = st.slider("Viabilidad financiera", 1, 5, 3)
            with col3: innovacion = st.slider("Innovación", 1, 5, 3)
            puntaje_total = rigor + viabilidad + innovacion
        else:
            col1, col2, col3 = st.columns(3)
            with col1: creatividad = st.slider("Creatividad", 1, 5, 3)
            with col2: claridad = st.slider("Claridad de la presentación", 1, 5, 3)
            with col3: impacto = st.slider("Impacto percibido", 1, 5, 3)
            puntaje_total = creatividad + claridad + impacto

        st.markdown(f"<div style='margin-top:10px;'>🧮 Puntaje total: <b>{puntaje_total}</b></div>", unsafe_allow_html=True)

        if st.button("✅ Enviar voto"):
            try:
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
                        st.warning("⚠️ Ya registraste un voto para este equipo.")
                        return

                registro = [str(datetime.now()), rol, correo, equipo_id, puntaje_total]
                ws_votos.append_row(registro)
                st.success("✅ ¡Tu voto ha sido registrado exitosamente!")
                st.balloons()
                st.session_state.validado_voto = False

            except Exception as e:
                st.error(f"⚠️ Error al registrar el voto: {e}")

        # 🔙 Botón para volver o votar otro equipo
        if st.button("🔙 Volver al inicio / Votar otro equipo"):
            st.session_state.validado_voto = False
            if "equipo_voto" in st.session_state:
                del st.session_state["equipo_voto"]
            st.rerun()

def modulo_resultados():
    st.markdown("""
    <div style="text-align:center; background:#fff8e6; border-left:6px solid #1B396A;
                padding:16px; border-radius:10px; color:#1B396A;">
        <div style="font-size:1.4em;">⚠️ Atención</div>
        <div>El sistema de votación estará disponible <b>solo durante el evento</b>.</div>
        <div>Escanea el QR y completa tu evaluación con <b>responsabilidad</b>.</div>
    </div>
    """, unsafe_allow_html=True)


# ======================================================
# 🔹 MAIN APP
# ======================================================
def main():
    st.set_page_config(page_title="Concurso Analítica Financiera", page_icon="📊", layout="wide")

    st.markdown("""
    <div style="height:10px; margin-bottom:15px;
      background:linear-gradient(270deg,#1B396A,#27ACE2,#1B396A,#27ACE2);
      background-size:600% 600%; animation:gradientAnim 6s ease infinite;
      border-radius:6px;"></div>
    <style>@keyframes gradientAnim {
      0% {background-position:0% 50%}
      50% {background-position:100% 50%}
      100% {background-position:0% 50%}
    }</style>
    """, unsafe_allow_html=True)

    if "rol" not in st.session_state:
        st.session_state.rol = None
    if "rol_seleccionado" not in st.session_state:
        st.session_state.rol_seleccionado = False

    with st.sidebar:
        st.image("https://es.catalat.org/wp-content/uploads/2020/09/fondo-editorial-itm-2020-200x200.png", width=140)
        st.markdown("<h3 style='color:white;'>Menú principal</h3>", unsafe_allow_html=True)

        if st.session_state.rol_seleccionado:
            if st.session_state.rol == "Docente":
                opcion = option_menu(
                    None, ["Home", "Inscripción", "Dashboard", "Votación", "Resultados"],
                    icons=["house", "file-earmark-text", "bar-chart", "check2-square", "trophy"],
                    styles={
                        "container": {"background-color": "#1B396A"},
                        "icon": {"color": "white"},
                        "nav-link": {"color": "white"},
                        "nav-link-selected": {"background-color": "#27ACE2", "color": "white"},
                    })
            else:
                opcion = option_menu(
                    None, ["Home", "Inscripción", "Votación", "Resultados"],
                    icons=["house", "file-earmark-text", "check2-square", "trophy"],
                    styles={
                        "container": {"background-color": "#1B396A"},
                        "icon": {"color": "white"},
                        "nav-link": {"color": "white"},
                        "nav-link-selected": {"background-color": "#27ACE2", "color": "white"},
                    })
        else:
            opcion = "Home"

    if opcion == "Home": modulo_home()
    elif opcion == "Inscripción": modulo_inscripcion()
    elif opcion == "Dashboard": modulo_dashboard()
    elif opcion == "Votación": modulo_votacion()
    elif opcion == "Resultados": modulo_resultados()


if __name__ == "__main__":
    main()



