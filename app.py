import streamlit as st
import pandas as pd
import gspread
import random
import string
import base64
from google.oauth2 import service_account
from datetime import datetime
import altair as alt
from streamlit_option_menu import option_menu
from email.mime.text import MIMEText
from googleapiclient.discovery import build

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
st.set_page_config(page_title="Concurso ITM", page_icon="🎓", layout="wide")

# Inicialización de variables de sesión
if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = False
if "correo_actual" not in st.session_state:
    st.session_state["correo_actual"] = ""
if "rol" not in st.session_state:
    st.session_state["rol"] = None

# ======================================================
# FUNCIONES DE APOYO
# ======================================================
def conectar_hoja(nombre_hoja):
    """Conecta con una hoja de Google Sheets"""
    creds = service_account.Credentials.from_service_account_info(st.secrets["gcp"])
    client = gspread.authorize(creds)
    return client.open("BD_CONCURSO_ITM").worksheet(nombre_hoja)

def generar_codigo():
    """Genera un código aleatorio de 6 dígitos"""
    return str(random.randint(100000, 999999))

def enviar_correo_gmail(service_account_info, destinatario, asunto, mensaje_html):
    """Simulación de envío de correo (puedes reemplazar con tu función real de Gmail API)"""
    st.info(f"📩 Correo enviado a **{destinatario}** con asunto: *{asunto}*")
    # Aquí colocarías el código real de envío usando la API de Gmail


# ======================================================
# MÓDULO DE LOGIN Y REGISTRO
# ======================================================
def modulo_login():
    st.title("🔐 Acceso al Portal del Concurso ITM")
    st.write("Por favor, inicia sesión o regístrate para continuar.")

    opcion = st.radio("Selecciona una opción", ["Iniciar sesión", "Registrarme"], horizontal=True)

    correo = st.text_input("📧 Correo institucional")

    if opcion == "Iniciar sesión":
        if st.button("Enviar código de acceso"):
            codigo = generar_codigo()
            st.session_state["codigo_enviado"] = codigo
            st.session_state["correo_temp"] = correo
            enviar_correo_gmail(st.secrets["gcp"], correo, "Código de acceso ITM",
                                f"<p>Tu código de acceso es: <b>{codigo}</b></p>")
            st.success("Se ha enviado un código a tu correo.")
        
        codigo_ingresado = st.text_input("Introduce el código recibido")

        if st.button("Validar código"):
            if codigo_ingresado == st.session_state.get("codigo_enviado") and correo == st.session_state.get("correo_temp"):
                st.session_state["usuario_autenticado"] = True
                st.session_state["correo_actual"] = correo
                st.session_state["rol"] = "Docente" if "profesor" in correo.lower() else "Estudiante"
                st.success("✅ Acceso concedido correctamente.")
                st.rerun()
            else:
                st.error("❌ Código incorrecto o expirado.")

    elif opcion == "Registrarme":
        rol = st.selectbox("Selecciona tu rol", ["Docente", "Estudiante"])
        if st.button("Registrar cuenta"):
            # Guardar en la hoja correspondiente
            hoja = conectar_hoja("usuarios")
            hoja.append_row([correo, rol])
            st.success("✅ Registro completado. Ahora puedes iniciar sesión.")
            st.session_state["rol"] = rol


# ======================================================
# MÓDULO HOME PRINCIPAL
# ======================================================
def modulo_home():
    st.markdown("## 🏫 Portal del Concurso ITM")

    correo = st.session_state.get("correo_actual", "****")
    rol = st.session_state.get("rol", "Sin rol")

    st.markdown(f"👋 Bienvenido **{correo}** — Rol: **{rol}**")

    if st.button("🚪 Cerrar sesión"):
        st.session_state["usuario_autenticado"] = False
        st.session_state["correo_actual"] = ""
        st.session_state["rol"] = None
        st.rerun()

    st.divider()
    st.markdown("### 📘 Menú principal")
    st.markdown("✅ Puedes acceder a inscripciones, votaciones y resultados según tu rol.")


# ======================================================
# MÓDULOS DE SECCIONES
# ======================================================
def modulo_inscripcion():
    st.title("📝 Inscripción de participantes")
    st.info("Formulario de inscripción disponible aquí.")

def modulo_votacion():
    st.title("🗳️ Sistema de votación")
    st.info("Aquí podrás votar durante el evento.")

def modulo_resultados():
    st.title("🏆 Resultados del concurso")
    st.info("Consulta los ganadores y estadísticas.")

def modulo_eventos():
    st.title("📅 Agenda del evento")
    st.info("Consulta los horarios y actividades.")

# ======================================================
# CONTROL DE ACCESO
# ======================================================
if not st.session_state["usuario_autenticado"]:
    modulo_login()
    st.stop()

# ======================================================
# MENÚ LATERAL PRINCIPAL (solo después de login)
# ======================================================
with st.sidebar:
    seleccion = option_menu(
        "Menú principal",
        ["Inicio", "Inscripción", "Votación", "Resultados", "Eventos"],
        icons=["house", "file-text", "check2-square", "trophy", "calendar"],
        menu_icon="cast",
        default_index=0,
    )

if seleccion == "Inicio":
    modulo_home()
elif seleccion == "Inscripción":
    modulo_inscripcion()
elif seleccion == "Votación":
    modulo_votacion()
elif seleccion == "Resultados":
    modulo_resultados()
elif seleccion == "Eventos":
    modulo_eventos()
