# app.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

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
    ws_docentes = sh.worksheet("Docentes")   # Hoja "Docentes"
    data = ws_docentes.get_all_records()
    return pd.DataFrame(data)

# ======================================================
# 🔹 MÓDULO INSCRIPCIÓN
# ======================================================

def modulo_inscripcion():
    st.header("Formulario de Inscripción")
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

# ======================================================
# 🔹 MÓDULO HOME
# ======================================================

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
        st.image(
            "https://media4.giphy.com/media/ZBoap6UCvOEeQNGzHK/200.webp",
            caption="¡Bienvenido!",
            use_container_width=True
        )

# ======================================================
# 🔹 MÓDULO VOTACIÓN
# ======================================================

def modulo_votacion():
    st.subheader("🗳 Votación de Equipos")

    rol = st.radio("Selecciona tu rol:", ["Docente", "Estudiante/Asistente"])
    correo = st.text_input("Ingresa tu correo institucional para validar el voto:")
    equipo_id = st.text_input("Ingresa el código del equipo a evaluar:")

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
            # Validar equipo
            df_insc = conectar_google_sheets(st.secrets)
            df_insc = preparar_dataframe(df_insc)
            if equipo_id not in df_insc["ID Equipo"].values:
                st.error("❌ El código de equipo no es válido")
                return

            # Si es docente → validar en hoja Docentes
            if rol == "Docente":
                df_docentes = cargar_docentes(st.secrets)
                if correo not in df_docentes["Correo"].values:
                    st.error("❌ Tu correo no está autorizado como jurado docente.")
                    return

            # Abrir hoja de votaciones
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp"], scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            gc = gspread.authorize(credentials)
            sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
            ws_votos = sh.worksheet("Votaciones")

            # Validar duplicados
            votos = pd.DataFrame(ws_votos.get_all_records())
            if not votos.empty:
                existe = votos[(votos["Correo"] == correo) & (votos["ID Equipo"] == equipo_id)]
                if not existe.empty:
                    st.error("❌ Ya registraste un voto para este equipo")
                    return

            # Guardar voto
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

def main():
    st.set_page_config(
        page_title="Concurso Analítica Financiera",
        page_icon="📊",
        layout="wide"
    )

    # 🔹 Banner superior animado
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

    # 🔹 Logo ITM
    st.markdown(
        f'<div style="display:flex;justify-content:center;margin-bottom:8px">'
        f'<img src="https://upload.wikimedia.org/wikipedia/commons/5/56/Logo_ITM.svg" '
        f'width="160" style="border-radius:10px;border:1px solid #ccc" /></div>',
        unsafe_allow_html=True
    )

    # 🔹 Títulos
    st.markdown(
        "<h1 style='text-align: center; color: #1B396A;'>🏆 Concurso Analítica Financiera ITM</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align: center; color: #27ACE2;'>¡Participa, aprende y gana!</h4>",
        unsafe_allow_html=True
    )

    # Inicialización de estado
    if 'active_tab' not in st.session_state: st.session_state.active_tab = 'Home'
    if 'rol' not in st.session_state: st.session_state.rol = None
    if 'rol_seleccionado' not in st.session_state: st.session_state.rol_seleccionado = False

    # HOME
    if st.session_state.active_tab == 'Home':
        modulo_home()
        if not st.session_state.rol_seleccionado or st.session_state.rol is None:
            st.warning("Por favor selecciona tu rol y presiona 'Continuar' para acceder al menú.")
            return

    # SIDEBAR
    with st.sidebar:
        st.header("Menú")
        if st.button("🏠 Home"):
            st.session_state.active_tab = 'Home'
            st.session_state.rol_seleccionado = False

        if st.session_state.rol_seleccionado:
            if st.session_state.rol == "Docente":
                if st.button("📝 Inscripción"): st.session_state.active_tab = 'Inscripción'
                if st.button("📊 Dashboard"): st.session_state.active_tab = 'Dashboard'
                if st.button("🗳 Votación"): st.session_state.active_tab = 'Votación'
                if st.button("📈 Resultados"): st.session_state.active_tab = 'Resultados'
            elif st.session_state.rol == "Estudiante":
                if st.button("📝 Inscripción"): st.session_state.active_tab = 'Inscripción'
                if st.button("🗳 Votación"): st.session_state.active_tab = 'Votación'
                if st.button("📈 Resultados"): st.session_state.active_tab = 'Resultados'

    # Router de módulos
    if st.session_state.active_tab == 'Inscripción':
        modulo_inscripcion()
    elif st.session_state.active_tab == 'Dashboard':
        modulo_dashboard()
    elif st.session_state.active_tab == 'Votación':
        modulo_votacion()
    elif st.session_state.active_tab == 'Resultados':
        modulo_resultados()
    elif st.session_state.active_tab == 'Home':
        st.info("Usa el menú lateral para navegar entre los módulos.")

if __name__ == "__main__":
    main()



