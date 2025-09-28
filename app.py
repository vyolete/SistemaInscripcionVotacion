# app.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import qrcode
from io import BytesIO
import base64

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
# 🔹 QR GENERATOR
# ======================================================
def generar_qr(data: str):
    qr = qrcode.QRCode(
        version=1,
        box_size=6,
        border=2
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def qr_to_base64(img):
    """Convierte la imagen QR en string base64 para insertarla en correos"""
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

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
    st.info("Al completar la inscripción recibirás un correo con el QR único de tu equipo.")

# ======================================================
# 🔹 MÓDULO DASHBOARD
# ======================================================
def mostrar_qr_equipos(df_filtrado):
    st.subheader("📲 Códigos QR por equipo")

    for _, row in df_filtrado.iterrows():
        equipo_id = row["ID Equipo"]
        equipo_nombre = row["Equipo"]

        # URL directa al módulo de votación (ajusta con tu dominio real de Streamlit)
        url_qr = f"https://tuapp.streamlit.app/?tab=Votación&equipo={equipo_id}"

        img = generar_qr(url_qr)
        buf = BytesIO()
        img.save(buf, format="PNG")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(buf.getvalue(), caption=f"QR {equipo_id}", width=120)
        with col2:
            st.markdown(f"**{equipo_nombre}** ({equipo_id})")
            st.write(f"[Abrir link directo al voto]({url_qr})")

def resumen_docente(df_filtrado):
    resumen = df_filtrado.groupby("Docente")['Cantidad de Estudiantes'].sum().reset_index()
    st.subheader("Resumen por docente")
    st.dataframe(resumen)
    return resumen

def detalle_inscripciones(df_filtrado):
    st.subheader("Detalle de inscripciones")
    st.dataframe(df_filtrado[['Equipo', 'Docente', 'Cantidad de Estudiantes', 'ID Equipo']])

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
    df['Cantidad de Estudiantes'] = df['Participantes'].apply(contar_participantes)

    detalle_inscripciones(df)
    resumen_docente(df)
    mostrar_qr_equipos(df)

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
        st.image("https://media4.giphy.com/media/ZBoap6UCvOEeQNGzHK/200.webp",
                 caption="¡Bienvenido!", use_container_width=True)

# ======================================================
# 🔹 MÓDULO VOTACIÓN
# ======================================================
def modulo_votacion():
    st.subheader("🗳 Votación de Equipos")

    # Leer parámetros de la URL
    query_params = st.query_params
    equipo_preseleccionado = query_params.get("equipo", [""])[0]

    rol = st.radio("Selecciona tu rol:", ["Docente", "Estudiante/Asistente"])
    correo = st.text_input("Ingresa tu correo institucional para validar el voto:")
    equipo_id = st.text_input("Ingresa el código del equipo a evaluar:", value=equipo_preseleccionado)

    if rol == "Docente":
        rigor = st.slider("Rigor técnico", 1, 5, 3)
        viabilidad = st.slider("Viabilidad financiera", 1, 5, 3)
        innovacion = st.slider("Innovación", 1, 5, 3)
        criterios = [rigor, viabilidad, innovacion]
    else:
        creatividad = st.slider("Creatividad", 1, 5, 3)
        claridad = st.slider("Claridad de la presentación", 1, 5, 3)
        impacto = st.slider("Impacto percibido", 1, 5, 3)
        criterios = [creatividad, claridad, impacto]

    puntaje_total = sum(criterios)

    if st.button("Enviar voto"):
        if not correo or not equipo_id:
            st.error("❌ Debes ingresar tu correo y el código de equipo")
            return

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
                    st.error("❌ Ya registraste un voto para este equipo")
                    return

            registro = [str(datetime.now()), rol, correo, equipo_id, "", *criterios, puntaje_total, hash(f"{correo}{equipo_id}")]
            ws_votos.append_row(registro)

            st.success("✅ ¡Tu voto ha sido registrado!")
            st.session_state["reset_voto"] = True
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Error al registrar el voto: {e}")

# ======================================================
# 🔹 MÓDULO RESULTADOS
# ======================================================
def modulo_resultados():
    st.info("Los resultados estarán disponibles al finalizar el evento.")

# ======================================================
# 🔹 MAIN APP
# ======================================================
def main():
    st.set_page_config(page_title="Concurso Analítica Financiera", page_icon="📊", layout="wide")

    # Inicialización
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 'Home'
    if 'rol' not in st.session_state:
        st.session_state.rol = None
    if 'rol_seleccionado' not in st.session_state:
        st.session_state.rol_seleccionado = False

    # Router de módulos
    tab = st.session_state.active_tab
    if tab == 'Home': modulo_home()
    elif tab == 'Inscripción': modulo_inscripcion()
    elif tab == 'Dashboard': modulo_dashboard()
    elif tab == 'Votación': modulo_votacion()
    elif tab == 'Resultados': modulo_resultados()

    # Sidebar
    with st.sidebar:
        st.header("Menú")
        if st.button("🏠 Home"): st.session_state.active_tab = 'Home'; st.session_state.rol_seleccionado = False
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

if __name__ == "__main__":
    main()


