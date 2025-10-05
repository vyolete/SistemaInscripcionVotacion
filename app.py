import streamlit as st
import pandas as pd
import gspread
import random
import string
import base64
from datetime import datetime
import altair as alt
from streamlit_option_menu import option_menu
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials


# ======================================================
# 🔹 CONFIGURACIÓN Y ESTILOS INSTITUCIONALES ITM
# ======================================================
st.markdown("""
<style>
/* ===== FUENTES ===== */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
    background-color: #ffffff !important;
    color: #1B396A !important;
}

/* ===== CONTENEDOR PRINCIPAL ===== */
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
    color: #1B396A !important;
    padding: 1.5rem !important;
}

/* ===== TEXTO GENERAL ===== */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #1B396A !important;
}

/* ===== TEXTOS SECUNDARIOS ===== */
small, .stCaption, .stMarkdown small, .stText {
    color: #3C4F76 !important;
}

/* ===== PLACEHOLDERS E INPUTS ===== */
input, textarea {
    color: #1B396A !important;
    background-color: #FFFFFF !important;
    border: 1.5px solid #1B396A !important;
    border-radius: 6px !important;
    padding: 0.5em !important;
}
input::placeholder, textarea::placeholder {
    color: #6C7A99 !important;
    opacity: 1 !important;
}

/* ===== BOTONES ===== */
.stButton>button, .stButton>button * {
    background-color: #1B396A !important;
    color: #FFFFFF !important;        /* 🔹 Forzamos texto blanco */
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 0.6em 1.4em !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(27,57,106,0.3) !important;
    text-align: center !important;
}

/* 🔹 Hover */
.stButton>button:hover, .stButton>button:hover * {
    background-color: #244A8F !important;
    color: #FFFFFF !important;        /* Reforzamos el blanco en hover */
    transform: scale(1.03);
    transition: all 0.2s ease-in-out;
}

/* 🔹 Estado activo o foco */
.stButton>button:active, .stButton>button:focus {
    outline: none !important;
    color: #FFFFFF !important;
    background-color: #162B57 !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B396A 0%, #244A8F 100%) !important;
    color: #FFFFFF !important;
    padding: 20px 15px;
    border-right: 2px solid #EAF3FF;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* ===== MENÚ PRINCIPAL ===== */
ul.nav.nav-pills li a {
    background-color: transparent !important;
    color: #EAF3FF !important;
    font-weight: 600 !important;
}
ul.nav.nav-pills li a:hover {
    background-color: rgba(255,255,255,0.2) !important;
}
ul.nav.nav-pills li a.active {
    background-color: #FFFFFF !important;
    color: #1B396A !important;
}

/* ===== TÍTULOS LOGIN ===== */
.titulo {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #1B396A !important;
    text-align: center !important;
    margin-bottom: 25px !important;
}

/* ===== RESPONSIVO ===== */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        padding: 10px !important;
    }
    .sidebar-logo {
        width: 90px;
    }
}
</style>
""", unsafe_allow_html=True)


# ======================================================
# 🔹 UTILIDADES: Conexión y operaciones con Google Sheets
# ======================================================
def conectar_google_sheets(secrets):
    """
    Conecta y devuelve un DataFrame con la hoja principal (Sheet1).
    Se espera que secrets incluya:
      - st.secrets["gcp"]: credenciales service account
      - st.secrets["spreadsheet"]["id"]: id del spreadsheet
    """

    # 🔹 Scopes correctos
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = service_account.Credentials.from_service_account_info(
        secrets["gcp"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sh = client.open_by_key(secrets["spreadsheet"]["id"])
    worksheet = sh.worksheet("Inscripción a un evento (respuestas)")
    data = worksheet.get_all_records()

    return pd.DataFrame(data)


def cargar_hoja_por_nombre(secrets, nombre_hoja):
    try:
        # Autenticación con la cuenta de servicio
        creds = service_account.Credentials.from_service_account_info(
            secrets["gcp"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(secrets["spreadsheet"]["id"])
        ws = sh.worksheet(nombre_hoja)
        df = pd.DataFrame(ws.get_all_records())
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar la hoja '{nombre_hoja}': {e}")
        return pd.DataFrame()

def guardar_fila_en_hoja(secrets, nombre_hoja, fila):
    creds = Credentials.from_service_account_info(
        secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sh = client.open_by_key(secrets["spreadsheet"]["id"])
    worksheet = sh.worksheet(nombre_hoja)
    worksheet.append_row(fila)

def preparar_dataframe(df):
    # Intentamos renombrar columnas si están con nombres largos
    rename_map = {}
    if "Nombre del Equipo" in df.columns:
        rename_map["Nombre del Equipo"] = "Equipo"
    if "Inscripción Participantes" in df.columns:
        rename_map["Inscripción Participantes"] = "Participantes"
    if "Docente" in df.columns:
        rename_map["Docente"] = "Docente"
    if "Id_equipo" in df.columns:
        rename_map["Id_equipo"] = "ID Equipo"
    if "ID Equipo" not in df.columns and "Id_equipo" in df.columns:
        rename_map["Id_equipo"] = "ID Equipo"
    df = df.rename(columns=rename_map)
    return df

def cargar_docentes(secrets):
    return cargar_hoja_por_nombre(secrets, "Docentes")

def contar_participantes(participantes_str):
    if not participantes_str:
        return 0
    estudiantes = [p.strip() for p in str(participantes_str).split(',') if p.strip()]
    return len(estudiantes)

def generar_codigo_docente():
    return "DOC-" + ''.join(random.choices(string.digits, k=4))

# ======================================================
# 🔹 Envío de correos con Gmail API
# ======================================================
def enviar_correo_gmail(destinatario, asunto, mensaje_html):
    """Envía un correo usando Gmail API con la service account (delegada si corresponde)."""
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp"],
            scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        # Nota: si se requiere delegación (actuar como un usuario real), usar creds.with_subject("user@domain")
        # Aquí asumimos que la cuenta de servicio tiene habilitado el acceso para enviar (o se delega)
        service = build("gmail", "v1", credentials=creds)

        mime_message = MIMEText(mensaje_html, "html")
        mime_message["to"] = destinatario
        mime_message["from"] = st.secrets["gmail"]["user"] if "gmail" in st.secrets and "user" in st.secrets["gmail"] else "me"
        mime_message["subject"] = asunto

        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        service.users().messages().send(userId="me", body=create_message).execute()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al enviar correo: {e}")
        return False

# ======================================================
# 🔹 MÓDULOS: Home, Inscripción, Dashboard, Votación, Resultados, Eventos
# ======================================================
def modulo_home():
    st.title("🏫 Portal del Concurso ITM")
    if "correo_usuario" in st.session_state and st.session_state.get("correo_usuario"):
        st.markdown(f"👋 Bienvenido **{st.session_state.get('correo_usuario')}** — Rol: **{st.session_state.get('rol_usuario', 'Invitado')}**")
    else:
        st.markdown("👋 Bienvenido — por favor inicia sesión para acceder al panel completo.")
    st.markdown("### 📘 Menú principal")
    st.write("✅ Puedes acceder a inscripciones, votaciones y resultados según tu rol.")

def modulo_inscripcion():
    st.header("📝 Formulario de Inscripción")
    st.markdown("Completa el formulario a través del siguiente módulo:")
    st.components.v1.iframe(
        "https://forms.gle/hzBPg4THxcD64ygK9",
        height=800,
        width="100%"
    )
    st.markdown(
        "Si el formulario no carga correctamente, da clic "
        "[aquí](https://forms.gle/hzBPg4THxcD64ygK9) para abrirlo directamente."
    )

def modulo_dashboard():
    st.header("📊 Dashboard de Inscripciones")
    try:
        df = conectar_google_sheets(st.secrets)
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        return

    if df.empty:
        st.warning("⚠️ No hay inscripciones registradas todavía.")
        return

    df = preparar_dataframe(df)
    docentes = df.get('Docente', pd.Series(["Sin docente"])).unique()
    docente_sel = st.sidebar.selectbox("📌 Filtrar por docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Inscripciones", len(df_filtrado))
    with col2:
        st.metric("👥 Equipos", df_filtrado.get('ID Equipo', pd.Series()).nunique())
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
        cols_to_show = [c for c in ['Equipo', 'Docente', 'Cantidad de Estudiantes', 'ID Equipo'] if c in df_filtrado.columns]
        st.dataframe(df_filtrado[cols_to_show])

def modulo_resultados():
    st.markdown("""
    <div style="text-align:center; background:#fff8e6; border-left:6px solid #1B396A;
                padding:16px; border-radius:10px; color:#1B396A;">
        <div style="font-size:1.4em;">⚠️ Atención</div>
        <div>El sistema de votación estará disponible <b>solo durante el evento</b>.</div>
        <div>Escanea el QR y completa tu evaluación con <b>responsabilidad</b>.</div>
    </div>
    """, unsafe_allow_html=True)

def modulo_eventos():
    st.markdown("<h2 style='color:#1B396A; text-align:center;'>📅 Próximo Evento</h2>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            st.image("data:image/jpeg;base64,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", use_container_width=True)
        except Exception:
            st.warning("⚠️ No se pudo cargar la imagen del conferencista.")
            st.image("https://media1.giphy.com/media/ZBoap6UCvOEeQNGzHK/200.webp", use_container_width=True)
    with col2:
        st.markdown("""
        <div style="color:#1B396A; font-family:'Segoe UI', sans-serif;">
            <h3 style="margin-bottom:0;">🎙️ Conferencista: <b>Carlos Naranjo</b></h3>
            <p style="font-size:15px; text-align:justify;">
                Magíster en Gestión de Organizaciones, especialista en Gerencia para Ingenieros del ITM e Ingeniero Informático.
            </p>
            <div style="background-color:#F3F7FB; border-left:4px solid #1B396A; padding:10px 15px; border-radius:8px; margin-top:10px;">
                <p style="margin:0;"><b>🗓️ Fecha:</b> Jueves 30 de octubre</p>
                <p style="margin:0;"><b>🕗 Hora:</b> 8:00 p.m.</p>
                <p style="margin:0;"><b>📍 Lugar:</b> Auditorio menor ITM - Sede Fraternidad, Barrio Boston, Medellín</p>
                <p style="margin:0;"><b>💬 Charla:</b> “¿Alguna vez te has preguntado cómo funcionan los robo-advisors y si realmente están transformando la forma de invertir?”</p>
                <p style="margin:0;"><b>🤝 Invitado especial:</b> Gerente de Bancolombia</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1B396A;'>🌟 ¡No te pierdas esta oportunidad de aprendizaje e inspiración! 🌟</p>", unsafe_allow_html=True)

# ======================================================
# 🔹 MÓDULO VOTACIÓN (mantengo exactamente tu código de votación)
# ======================================================
def modulo_votacion():
    st.header("🗳 Votación de Equipos")

    # --- Leer parámetros de la URL (st.query_params devuelve listas) ---
    params = st.query_params  # Map<string, list>
    # Tomamos el primer valor si existe, y limpiamos espacios
    equipo_qr = None
    if "equipo" in params:
        val = params.get("equipo")
        if isinstance(val, (list, tuple)) and len(val) > 0:
            equipo_qr = str(val[0]).strip()
        elif isinstance(val, str):
            equipo_qr = val.strip()

    rol_qr = None
    if "rol" in params:
        val = params.get("rol")
        if isinstance(val, (list, tuple)) and len(val) > 0:
            rol_qr = str(val[0]).strip().lower()
        elif isinstance(val, str):
            rol_qr = val.strip().lower()

    # --- Cargar inscripciones y preparar df para buscar nombre del equipo ---
    try:
        df_insc = conectar_google_sheets(st.secrets)
        df_insc = preparar_dataframe(df_insc)  # Asegúrate que esta función renombra la columna a 'ID Equipo'
    except Exception as e:
        st.error(f"❌ Error al cargar inscripciones: {e}")
        return

    # Normalizamos la columna de IDs a string y sin espacios para comparar
    if "ID Equipo" in df_insc.columns:
        df_insc["ID Equipo"] = df_insc["ID Equipo"].astype(str).str.strip()
    else:
        st.error("❌ La hoja de inscripciones no tiene la columna 'ID Equipo'. Revisa nombres de columnas.")
        return

    equipos_validos = set(df_insc["ID Equipo"].tolist())

    # --- Si vino equipo en URL, mostrar mensaje y buscar nombre ---
    if equipo_qr:
        if equipo_qr in equipos_validos:
            nombre_equipo = None
            if "Equipo" in df_insc.columns:
                matched = df_insc[df_insc["ID Equipo"] == equipo_qr]
                if not matched.empty:
                    nombre_equipo = matched.iloc[0]["Equipo"]
            msg = f"📲 Ingreso directo: estás votando por el equipo **{equipo_qr}**"
            if nombre_equipo:
                msg += f" — **{nombre_equipo}**"
            st.success(msg)
        else:
            st.error(f"⚠️ El código del equipo en la URL ({equipo_qr}) no es válido.")

    # --- Estado de validación (un flujo en dos fases) ---
    if "validado_voto" not in st.session_state:
        st.session_state.validado_voto = False

    # Fase 1: pedir rol/correo/código (si no validado aún)
    if not st.session_state.validado_voto:
        if rol_qr:
            rol = "Docente" if rol_qr.lower().startswith("doc") else "Estudiante / Asistente"
            st.info(f"👤 Rol detectado automáticamente: **{rol}**")
        else:
            rol = st.radio("Selecciona tu rol:", ["Estudiante / Asistente", "Docente"], horizontal=True)

        correo = st.text_input("📧 Correo institucional:")
        equipo_id = st.text_input("🏷️ Código del equipo a evaluar:", value=(equipo_qr or ""))

        if st.button("Continuar ▶️"):
            if not correo or not equipo_id:
                st.error("❌ Debes ingresar tu correo y el código del equipo.")
            else:
                equipo_id = str(equipo_id).strip()
                if equipo_id not in equipos_validos:
                    st.error("❌ El código del equipo no existe. Revisa el código o escanea el QR correcto.")
                else:
                    if "Docente" in rol:
                        try:
                            df_docentes = cargar_docentes(st.secrets)
                            if "Correo" in df_docentes.columns:
                                correos_doc = df_docentes["Correo"].astype(str).str.strip().tolist()
                            else:
                                st.error("❌ La hoja 'Docentes' no tiene la columna 'Correo'.")
                                return
                            if correo.strip() not in correos_doc:
                                st.error("❌ Tu correo no está autorizado como jurado docente. Solicita registro.")
                                return
                        except Exception as e:
                            st.error(f"❌ Error al validar docente: {e}")
                            return

                    st.session_state.validado_voto = True
                    st.session_state.rol_voto = rol
                    st.session_state.correo_voto = correo.strip()
                    st.session_state.equipo_voto = equipo_id
                    st.success("✅ Validación exitosa. Puedes proceder a evaluar.")
                    st.rerun()

    # Fase 2: formulario de votación (ya validado)
    else:
        rol = st.session_state.rol_voto
        correo = st.session_state.correo_voto
        equipo_id = st.session_state.equipo_voto

        # --- Antes de mostrar sliders: consultamos si ya votó ---
        try:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp"], scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
            ws_votos = sh.worksheet("Votaciones")
            votos = pd.DataFrame(ws_votos.get_all_records())  # puede estar vacío

            ya_voto = False
            if not votos.empty:
                votos["Correo"] = votos["Correo"].astype(str).str.strip()
                votos["ID Equipo"] = votos["ID Equipo"].astype(str).str.strip()
                existe = votos[(votos["Correo"] == correo) & (votos["ID Equipo"] == equipo_id)]
                if not existe.empty:
                    ya_voto = True
        except Exception as e:
            st.error(f"⚠️ Error al leer la hoja de votaciones: {e}")
            return

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#1B396A;'>📋 Evaluación del Proyecto — Equipo {equipo_id} ({rol})</h4>", unsafe_allow_html=True)

        if ya_voto:
            st.warning(f"⚠️ Ya registraste un voto para el equipo **{equipo_id}** con el correo **{correo}**.")
            if st.button("🔄 Votar por otro equipo"):
                st.session_state.validado_voto = False
                if "equipo_voto" in st.session_state: del st.session_state["equipo_voto"]
                st.rerun()
            return

        if "Docente" in rol:
            col1, col2, col3 = st.columns(3)
            with col1:
                rigor = st.slider("Rigor técnico", 1, 5, 3)
            with col2:
                viabilidad = st.slider("Viabilidad financiera", 1, 5, 3)
            with col3:
                innovacion = st.slider("Innovación", 1, 5, 3)
            puntaje_total = rigor + viabilidad + innovacion
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                creatividad = st.slider("Creatividad", 1, 5, 3)
            with col2:
                claridad = st.slider("Claridad de la presentación", 1, 5, 3)
            with col3:
                impacto = st.slider("Impacto percibido", 1, 5, 3)
            puntaje_total = creatividad + claridad + impacto

        st.markdown(f"<div style='margin-top:10px;'>🧮 Puntaje total: <b>{puntaje_total}</b></div>", unsafe_allow_html=True)

        if st.button("✅ Enviar voto"):
            try:
                registro = [str(datetime.now()), rol, correo, equipo_id, puntaje_total]
                ws_votos.append_row(registro)
                st.success("✅ ¡Tu voto ha sido registrado exitosamente!")
                st.balloons()
                st.session_state.validado_voto = False
            except Exception as e:
                st.error(f"⚠️ Error al registrar el voto: {e}")

        if st.button("🔙 Volver / Votar otro equipo"):
            st.session_state.validado_voto = False
            if "equipo_voto" in st.session_state:
                    del st.session_state["equipo_voto"]
            st.rerun()


# ======================================================
# 🔐 MÓDULO DE LOGIN REGISTRO DE USUARIOS
# =====================================================
def login_general():
    import streamlit as st
    import gspread
    from google.oauth2 import service_account

    # ======================================================
    # 🔹 CONEXIÓN GOOGLE SHEETS
    # ======================================================
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    client = gspread.authorize(credentials)

    # ======================================================
    # 🔹 INTERFAZ
    # ======================================================
    st.markdown("<h2 style='color:#1B396A;'>🔐 Acceso al Sistema del Concurso ITM</h2>", unsafe_allow_html=True)
    rol = st.radio("Selecciona tu rol:", ["Docente", "Estudiante"], horizontal=True)
    email = st.text_input("📧 Correo institucional:")

    # ======================================================
    # 🔹 FUNCIONES AUXILIARES
    # ======================================================
    def es_correo_itm(correo):
        return correo.endswith("@correo.itm.edu.co") or correo.endswith("@itm.edu.co")

    def buscar_correo(hoja, correo):
        try:
            dataframe = conectar_google_sheets(st.secrets)
            correos = [c.strip().lower() for c in ws.col_values(1)[1:]]  # omitir encabezado
            return correo.lower() in correos
        except Exception as e:
            st.error(f"⚠️ No se pudo acceder a la hoja {hoja}: {e}")
            return False

    # ======================================================
    # 🔹 DOCENTE
    # ======================================================
    if rol == "Docente":
        if st.button("Ingresar como Docente"):
            if not email:
                st.warning("Ingrese su correo institucional.")
                st.stop()
            if not es_correo_itm(email):
                st.error("Solo se permiten correos institucionales del ITM.")
                st.stop()

            # 1️⃣ Validar si está autorizado
            if not buscar_correo("Correos Autorizados", email):
                st.error("❌ Este correo no está autorizado. Solicite acceso al coordinador académico.")
                st.stop()

            # 2️⃣ Si está autorizado, validar si ya está registrado
            if not buscar_correo("Docentes", email):
                st.info("Correo autorizado pero no registrado.")
                codigo = st.text_input("Ingrese el código de validación enviado a su correo")
                if st.button("Registrar nuevo docente"):
                    if not codigo.strip():
                        st.warning("Debe ingresar un código de validación.")
                        st.stop()
                    hoja_docentes = client.open("Docentes").worksheet("Docentes")
                    hoja_docentes.append_row([email, codigo])
                    st.success("✅ Registro completado. Ya puede ingresar.")
                    st.stop()
            else:
                st.info("Este correo ya está registrado. Verifique su código de validación.")
                codigo = st.text_input("Ingrese su código de validación:")
                if st.button("Validar e ingresar"):
                    hoja_docentes = client.open("Docentes").worksheet("Docentes")
                    datos = hoja_docentes.get_all_records()
                    for fila in datos:
                        if fila.get("Correo", "").lower() == email.lower():
                            if str(fila.get("Codigo", "")).strip() == codigo.strip():
                                st.success(f"Bienvenido docente {email}")
                                st.session_state["usuario"] = email
                                st.session_state["rol"] = "Docente"
                                st.session_state["autenticado"] = True
                                st.switch_page("home_docente.py")
                                st.stop()
                    st.error("❌ Código de validación incorrecto.")
                    st.stop()

    # ======================================================
    # 🔹 ESTUDIANTE
    # ======================================================
    if rol == "Estudiante":
        if st.button("Ingresar como Estudiante"):
            if not email:
                st.warning("Ingrese su correo institucional.")
                st.stop()
            if not es_correo_itm(email):
                st.error("Solo se permiten correos institucionales del ITM.")
                st.stop()

            if not buscar_correo("Estudiantes", "Estudiantes", email):
                st.info("Correo no encontrado. Puede registrarse a continuación.")
                if st.button("Registrar nuevo estudiante"):
                    hoja_estudiantes = client.open("Estudiantes").worksheet("Estudiantes")
                    hoja_estudiantes.append_row([email])
                    st.success("✅ Registro exitoso. Ya puede iniciar sesión.")
                    st.stop()
            else:
                st.success(f"Bienvenido estudiante {email}")
                st.session_state["usuario"] = email
                st.session_state["rol"] = "Estudiante"
                st.session_state["autenticado"] = True
                st.switch_page("home_estudiante.py")
                st.stop()



# ======================================================
# 🔹 FUNCIÓN PRINCIPAL
# ======================================================
def main():
    st.set_page_config(page_title="Concurso Analítica Financiera ITM", layout="wide")

    # --- Inicializar variables de sesión ---
    if "logueado" not in st.session_state:
        st.session_state["logueado"] = False
    if "rol" not in st.session_state:
        st.session_state["rol"] = "Invitado"
    if "correo_actual" not in st.session_state:
        st.session_state["correo_actual"] = ""

    # --- Título institucional (siempre visible) ---
    st.markdown("""
        <style>
        .titulo-principal {
            color: #1B396A;
            font-weight: 700;
            text-align: center;
            font-size: 1.8rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        </style>
        <div class="titulo-principal">🏫 Concurso de Analítica Financiera ITM</div>
    """, unsafe_allow_html=True)

    # --- Si NO hay sesión iniciada: mostrar login y ocultar menú ---
    if not st.session_state["logueado"]:
        with st.container():
            st.markdown("<div style='text-align:center; margin-top:30px;'>", unsafe_allow_html=True)
            st.image("https://media1.giphy.com/media/ZBoap6UCvOEeQNGzHK/200.webp", width=160)
            st.markdown("<h3 style='color:#1B396A;'>🔐 Acceso al Sistema</h3>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            correo = st.text_input("📧 Ingresa tu correo institucional:")
            rol = st.radio("Selecciona tu rol:", ["Estudiante / Asistente", "Docente"], horizontal=True)

            if st.button("Ingresar"):
                if correo.endswith("@correo.itm.edu.co"):
                    st.session_state["correo_actual"] = correo
                    st.session_state["rol"] = "Docente" if rol == "Docente" else "Estudiante"
                    st.session_state["logueado"] = True
                    st.success("Inicio de sesión exitoso.")
                    st.rerun()
                else:
                    st.error("❌ Usa tu correo institucional @correo.itm.edu.co")
        return  # ← Evita que cargue el menú si no hay login

    # ======================================================
    # 🔹 MENÚ LATERAL PRINCIPAL (solo visible si hay login)
    # ======================================================
    with st.sidebar:
        st.image("https://repositorio.itm.edu.co/assets/custom/images/logo.png", width=120)
        st.markdown("---")
        st.markdown(f"👤 **Usuario:** {st.session_state['correo_actual']}")
        st.markdown(f"🧩 **Rol:** {st.session_state['rol']}")
        st.markdown("---")

        # 🔹 MENÚ SEGÚN ROL (versión institucional azul)
        if st.session_state["rol"] == "Docente":
            opciones = ["Inicio", "Inscripción", "Votación", "Dashboard", "Resultados", "Eventos"]
            iconos = ["house", "clipboard2-data", "check2-square", "bar-chart", "trophy", "calendar-event"]
        else:  # Estudiante / Asistente
            opciones = ["Inicio", "Inscripción", "Votación", "Resultados", "Eventos"]
            iconos = ["house", "clipboard2-data", "check2-square", "trophy", "calendar-event"]

        seleccion = option_menu(
            "📘 Menú Principal",
            opciones,
            icons=iconos,
            menu_icon="cast",
            default_index=0,
            styles={
                # Fondo azul institucional ITM
                "container": {
                    "background-color": "#1B396A",
                    "padding": "10px",
                    "border-radius": "8px",
                },
                # Iconos
                "icon": {
                    "color": "#FFFFFF",
                    "font-size": "18px",
                },
                # Enlaces del menú
                "nav-link": {
                    "color": "#E6EAF0",
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px 0",
                    "border-radius": "6px",
                    "transition": "all 0.3s ease",
                },
                # Hover
                "nav-link:hover": {
                    "background-color": "#244A8F",
                    "color": "#FFFFFF",
                },
                # Opción seleccionada
                "nav-link-selected": {
                    "background-color": "#FFFFFF",
                    "color": "#1B396A",
                    "font-weight": "700",
                    "border-left": "4px solid #1B396A",
                    "box-shadow": "0 2px 6px rgba(0,0,0,0.15)",
                },
                # Título del menú
                "menu-title": {
                    "font-size": "18px",
                    "font-weight": "700",
                    "color": "#FFFFFF",
                    "margin-bottom": "10px",
                },
            },
        )


        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            st.session_state["logueado"] = False
            st.session_state["correo_actual"] = ""
            st.session_state["rol"] = "Invitado"
            st.success("Sesión cerrada correctamente.")
            st.rerun()

    # ======================================================
    # 🔹 RUTEO DE MÓDULOS SEGÚN SELECCIÓN
    # ======================================================
    if seleccion == "Inicio":
        modulo_home()
    elif seleccion == "Inscripción":
        modulo_inscripcion()
    elif seleccion == "Dashboard":
        if st.session_state["rol"] == "Docente":
            modulo_dashboard()
        else:
            st.warning("⚠️ Solo los docentes pueden acceder al Dashboard.")
    elif seleccion == "Votación":
        if st.session_state["rol"] != "Docente":
            modulo_votacion()
        else:
            st.warning("⚠️ Solo los estudiantes pueden acceder a la votación.")
    elif seleccion == "Resultados":
        modulo_resultados()
    elif seleccion == "Eventos":
        modulo_eventos()


# ======================================================
# 🔹 EJECUCIÓN PRINCIPAL
# ======================================================
if __name__ == "__main__":
    main()
