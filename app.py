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
        # Intenta abrir la hoja Docentes
        ws_docentes = sh.worksheet("Docentes")
        data = ws_docentes.get_all_records()
        return pd.DataFrame(data)



# ======================================================
# 🔹 MÓDULOS
# ======================================================

import streamlit as st

def init_session_state():
    defaults = {
        "rol": None,
        "rol_seleccionado": False,
        "validando_docente": False,
        "correo_docente": "",
        "correo_valido": False,
        "codigo_validado": False,
        "df_docentes": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_role():
    for k in ["rol", "rol_seleccionado", "validando_docente", "correo_docente", "correo_valido", "codigo_validado", "df_docentes"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


def render_student_ui():
    st.header("🎓 Panel - Estudiante")
    st.markdown("¡Bienvenido estudiante! Aquí tienes las opciones disponibles:")
    opcion = st.radio("Selecciona una opción:", ["Mi inscripción", "Mi equipo", "Votaciones", "Ayuda"])
    if opcion == "Mi inscripción":
        st.write("Mostrar formulario/estado de inscripción del estudiante...")
        # ejemplo: st.button("Inscribirme")
    elif opcion == "Mi equipo":
        st.write("Información del equipo, integrantes y código del equipo...")
    elif opcion == "Votaciones":
        st.write("Acceso a la sección de votación (si aplica).")
    else:
        st.write("FAQs, contacto o tutoriales.")

    if st.button( "Cerrar sesión"):
        reset_role()

def render_docente_ui():
    st.header("👨‍🏫 Panel - Docente")
    st.markdown("Bienvenido docente. Aquí están las herramientas del docente revisa el menu lateral izquierdo:")
    opcion = st.radio("Selecciona una opción:", ["Validar inscripciones", "Reportes", "Mi perfil", "Ayuda"])
    if opcion == "Validar inscripciones":
        st.write("Lista de inscripciones pendientes para validar...")
    elif opcion == "Reportes":
        st.write("Descargar reportes y métricas del concurso...")
    elif opcion == "Mi perfil":
        st.write(f"Correo: {st.session_state.get('correo_docente')}")
    else:
        st.write("Soporte y documentación para docentes.")

    if st.button("Cerrar sesión"):
        reset_role()

def modulo_home():
    init_session_state()

    # Cabecera
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://media1.giphy.com/media/ZBoap6UCvOEeQNGzHK/200.webp", width=180)

    st.markdown("<h1 style='text-align:center;'>🏆 Concurso Analítica Financiera ITM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>¡Participa, aprende y gana!</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>Selecciona tu rol para comenzar:</h4>", unsafe_allow_html=True)

    # Si aún no se ha seleccionado rol y no estamos validando docente: mostrar botones principales
    if not st.session_state["rol_seleccionado"] and not st.session_state["validando_docente"]:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🎓 Soy Estudiante", use_container_width=True):
                st.session_state["rol"] = "Estudiante"
                st.session_state["rol_seleccionado"] = True
                st.success("✅ Rol seleccionado: Estudiante")
                st.rerun()

        with c2:
            if st.button("👨‍🏫 Soy Docente", use_container_width=True):
                st.session_state["validando_docente"] = True
                st.rerun()


    # Flujo de validación de docente (correo -> código)
        # ======================================================
    # 🔹 VALIDACIÓN DE DOCENTE (correo + código)
    # ======================================================
    if st.session_state["validando_docente"]:
        # Encabezado con mejor formato
        st.markdown("""
            <div style='text-align:center; margin-top:20px;'>
                <h2 style='color:#1B396A;'>👨‍🏫 Validación Docente</h2>
                <p style='font-size:17px;'>
                    Ingresa tu correo institucional del ITM para validar tu acceso como docente.<br>
                    Si no estás autorizado, podrás volver al inicio.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Campo para correo
        correo_input = st.text_input(
            "📧 Ingresa tu correo institucional:",
            value=st.session_state.get("correo_docente", ""),
            placeholder="ejemplo@itm.edu.co"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            validar_correo = st.button("✅ Validar correo", use_container_width=True)
        with col2:
            volver_inicio = st.button("⬅️ Volver al inicio", use_container_width=True)

        # Acción: volver
        if volver_inicio:
            reset_role()
            st.rerun()

        # Acción: validar correo
        if validar_correo:
            df_docentes = cargar_docentes(st.secrets)
            if correo_input in df_docentes["Correo"].values:
                st.session_state["correo_docente"] = correo_input
                st.session_state["correo_valido"] = True
                st.session_state["df_docentes"] = df_docentes
                st.success("✅ Correo verificado. Ingresa tu código de validación. 👨‍🏫")
            else:
                st.error("❌ Tu correo no está autorizado como docente.")
                st.info("Puedes volver al inicio si ingresaste un correo incorrecto.")

        # Si el correo fue validado correctamente
        volver_inicio2= False
        if st.session_state.get("correo_valido", False):
            if "codigo_validado" not in st.session_state:
                st.session_state["codigo_validado"] = False

            st.markdown("---")
            st.markdown("<h4 style='color:#1B396A;'>🔐 Ingresa tu código de validación:</h4>", unsafe_allow_html=True)
            codigo_input = st.text_input("Código de validación:", placeholder="Ejemplo: ITM2025DOC")

            col1, col2 = st.columns([1, 1])
            with col1:
                validar_codigo = st.button("Verificar código ✅", use_container_width=True)

            if volver_inicio2:
                reset_role()
                st.rerun()

            if validar_codigo and not st.session_state["codigo_validado"]:
                df_docentes = st.session_state["df_docentes"]
                correo = st.session_state["correo_docente"]
                codigo_real = df_docentes.loc[df_docentes["Correo"] == correo, "Codigo"].values[0]

                if str(codigo_input).strip() == str(codigo_real).strip():
                    st.session_state["rol_seleccionado"] = True
                    st.session_state["rol"] = "Docente"
                    st.session_state["validando_docente"] = False
                    st.session_state["codigo_validado"] = True
                    st.success("✅ Acceso autorizado. Bienvenido docente. Revisa los ítems del menú 👨‍🏫")
                    st.toast("👨‍🏫 Acceso docente habilitado correctamente.")
                    st.rerun()
                else:
                    st.error("❌ Código incorrecto. Intenta nuevamente.")
                    reset_role()

    # Si ya se seleccionó un rol, mostrar la vista correspondiente
    if st.session_state.get("rol_seleccionado", False):
        if st.session_state.get("rol") == "Estudiante":
            render_student_ui()
        elif st.session_state.get("rol") == "Docente":
            render_docente_ui()
        else:
            st.warning("Rol desconocido. Reiniciando selección.")
            reset_role()

# Para probar localmente llamar a module_home()
# module_home()
     


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

def conectar_hoja_dashboard(secrets):
    """
    Conecta directamente a la hoja 'Respuestas de formulario 1' del Google Sheet.
    Retorna un DataFrame limpio.
    """
    try:
        worksheet = sh.worksheet("Respuestas de formulario 1")
    except gspread.WorksheetNotFound:
        st.error("❌ No se encontró la hoja 'Respuestas de formulario 1'.")
        st.stop()

    # Obtener datos y convertir a DataFrame
    respuestas = worksheet.get_all_records()
    df_resp = pd.DataFrame(respuestas)

    # Limpiar nombres de columna y renombrar para consistencia
     df_resp.columns =  df_resp.columns.str.strip()
     df_resp.rename(columns={
        'Inscripción Participantes': 'Participantes',
        'Id_equipo (Respuestas de formulario 1)': 'ID Equipo',
        'Nombre del Equipo': 'Equipo'
    }, inplace=True)

        return  df_resp

def modulo_dashboard():
    st.header("📊 Dashboard de Inscripciones")

    # Cargar solo la hoja necesaria
    try:
        df = conectar_hoja_dashboard(st.secrets)
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja: {e}")
        st.stop()

    if df.empty:
        st.warning("⚠️ No hay inscripciones registradas todavía.")
        return

    # Verificar que existan columnas necesarias
    required_cols = ['Docente', 'Participantes', 'ID Equipo', 'Equipo']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ La columna '{col}' no existe en el DataFrame.")
            st.write("Columnas disponibles:", df.columns.tolist())
            st.stop()

    # Selector de docente en sidebar
    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("📌 Filtrar por docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]

    # Calcular cantidad de estudiantes
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Inscripciones", len(df_filtrado))
    with col2:
        st.metric("👥 Equipos", df_filtrado['ID Equipo'].nunique())
    with col3:
        st.metric("🎓 Estudiantes", df_filtrado['Cantidad de Estudiantes'].sum())

    # Gráfico de inscripciones por docente
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

    # Detalle de inscripciones
    with st.expander("📋 Ver detalle de inscripciones", expanded=False):
        st.dataframe(df_filtrado[['Equipo', 'Docente', 'Cantidad de Estudiantes', 'ID Equipo']])

def modulo_dashboard():
    st.header("📊 Dashboard de Inscripciones")

    # Conectar con Google Sheets
    try:
        df = conectar_google_sheets(st.secrets)
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        st.stop()

    if df.empty:
        st.warning("⚠️ No hay inscripciones registradas todavía.")
        return

    # Limpiar nombres de columnas de espacios invisibles
    df.columns = df.columns.str.strip()

    # Renombrar columnas para que coincidan con tu código
    df.rename(columns={
        'Inscripción Participantes': 'Participantes',
        'Id_equipo (Respuestas de formulario 1)': 'ID Equipo',
        'Nombre del Equipo': 'Equipo'
    }, inplace=True)

    # Preparar DataFrame (tu función existente)
    df = preparar_dataframe(df)

    # Verificar que existan las columnas necesarias
    required_cols = ['Docente', 'Participantes', 'ID Equipo', 'Equipo']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ La columna '{col}' no existe en el DataFrame.")
            st.write("Columnas disponibles:", df.columns.tolist())
            st.stop()

    # Selector de docente en sidebar
    docentes = df['Docente'].unique()
    docente_sel = st.sidebar.selectbox("📌 Filtrar por docente", ["Todos"] + list(docentes))
    df_filtrado = df if docente_sel == "Todos" else df[df['Docente'] == docente_sel]

    # Calcular cantidad de estudiantes
    df_filtrado['Cantidad de Estudiantes'] = df_filtrado['Participantes'].apply(contar_participantes)

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Inscripciones", len(df_filtrado))
    with col2:
        st.metric("👥 Equipos", df_filtrado['ID Equipo'].nunique())
    with col3:
        st.metric("🎓 Estudiantes", df_filtrado['Cantidad de Estudiantes'].sum())

    # Gráfico de inscripciones por docente
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

    # Detalle de inscripciones
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
                # ========= FORMULARIO DE VOTACIÓN =========
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#1B396A;'>📋 Evaluación del Proyecto ({rol})</h4>", unsafe_allow_html=True)
        
        try:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp"], scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            gc = gspread.authorize(credentials)
            sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
            ws_votos = sh.worksheet("Votaciones")
        
            # Consultar si ya votó este usuario por este equipo
            votos = pd.DataFrame(ws_votos.get_all_records())
            ya_voto = False
            if not votos.empty:
                ya_voto = not votos[
                    (votos["Correo"] == correo) & (votos["ID Equipo"] == equipo_id)
                ].empty
        
            # ========= CASO 1: Ya votó =========
            if ya_voto:
                st.warning(f"⚠️ Ya registraste un voto para el equipo **{equipo_id}**.")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Votar por otro equipo"):
                    st.info("✅ Reiniciando para nuevo voto...")
                    st.session_state.validado_voto = False
                    if "equipo_voto" in st.session_state:
                        del st.session_state["equipo_voto"]
                    st.rerun()
        
            # ========= CASO 2: Puede votar =========
            else:
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
        
                st.markdown(
                    f"<div class='score-box'>🧮 Puntaje total: <b>{puntaje_total}</b></div>",
                    unsafe_allow_html=True
                )
        
                # ========= BOTÓN DE ENVÍO CON ANIMACIÓN =========
                if st.button("✅ Enviar voto"):
                    with st.spinner("🎯 Enviando tu voto al sistema... por favor espera unos segundos"):
                        import time
                        time.sleep(1.8)  # Simula procesamiento visual
        
                        try:
                            registro = [str(datetime.now()), rol, correo, equipo_id, puntaje_total]
                            ws_votos.append_row(registro)
                            st.success("✅ ¡Tu voto ha sido registrado exitosamente!")
                            st.balloons()
        
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("🔄 Votar por otro equipo"):
                                st.info("✅ Reiniciando para nuevo voto...")
                                st.session_state.validado_voto = False
                                if "equipo_voto" in st.session_state:
                                    del st.session_state["equipo_voto"]
                                st.rerun()
        
                        except Exception as e:
                            st.error(f"⚠️ Error al registrar el voto: {e}")
        
        except Exception as e:
            st.error(f"⚠️ Error al cargar datos de votaciones: {e}")

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
        st.markdown(
            """
            <a href="https://ibb.co/fYBV6nqY">
                <img src="https://i.ibb.co/4Z9wvYKZ/carlosnaranjo.jpg" alt="carlosnaranjo" border="0" style="width:100%; border-radius:10px;">
            </a>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown("""
        <div style="color:#1B396A; font-family:'Segoe UI', sans-serif;">
            <h3 style="margin-bottom:0;">🎙️ Conferencista: <b>Carlos Naranjo</b></h3>
            <p style="font-size:15px; text-align:justify;">
                Magíster en Gestión de Organizaciones, especialista en Gerencia para Ingenieros e Ingeniero Informático. 
                Como Gerente de Monitoreo de Canales, ha liderado la integración de tecnologías e inteligencia artificial 
                en procesos financieros, demostrando cómo la innovación puede transformar los retos en oportunidades. 
                Su propósito es inspirar a las nuevas generaciones a aprovechar la tecnología como motor de cambio y crecimiento.
            </p>
            <div style="background-color:#F3F7FB; border-left:4px solid #1B396A; padding:10px 15px; border-radius:8px; margin-top:10px;">
                <p style="margin:0;"><b>🗓️ Fecha:</b> Jueves 30 de octubre</p>
                <p style="margin:0;"><b>🕗 Hora:</b> 8:00 p.m.</p>
                <p style="margin:0;"><b>📍 Lugar:</b> Auditorio menor ITM - Sede Fraternidad, Barrio Boston, Medellín</p>
                <p style="margin:0;"><b>💬 Charla:</b> “¿Alguna vez te has preguntado cómo funcionan los robo-advisors y si realmente están transformando la forma de invertir?”</p>
                <p style="margin:0;"><b>🤝 Invitado especial:</b> Representante de Bancolombia</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1B396A;'>🌟 ¡No te pierdas esta oportunidad de aprendizaje e inspiración! 🌟</p>", unsafe_allow_html=True)


# ======================================================
# 🔹 MAIN APP
# ======================================================
def main():
    st.set_page_config(page_title="🏫 Portal del Concurso ITM Analítica Financiera", page_icon="📊", layout="wide")

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
                    None, ["Home", "Inscripción", "Dashboard", "Votación", "Resultados","Eventos"],
                    icons=["house", "file-earmark-text", "bar-chart", "check2-square", "trophy"],
                    styles={
                        "container": {"background-color": "#1B396A"},
                        "icon": {"color": "white"},
                        "nav-link": {"color": "white"},
                        "nav-link-selected": {"background-color": "#27ACE2", "color": "white"},
                    })
            else:
                opcion = option_menu(
                    None, ["Home", "Inscripción", "Votación", "Resultados","Eventos"],
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
    elif opcion == "Eventos": modulo_eventos()



if __name__ == "__main__":
    main()



