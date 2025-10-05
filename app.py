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

import streamlit as st
import gspread
import random
from google.oauth2 import service_account
from streamlit_option_menu import option_menu

def conectar_hoja(nombre_hoja):
    # Autenticación con la sección [gcp] de secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(credentials)
    
    # Abrir la hoja por ID
    spreadsheet_id = st.secrets["spreadsheet"]["id"]
    sh = client.open_by_key(spreadsheet_id)
    return sh.worksheet(nombre_hoja)

# ======================================================
# FUNCIONES AUXILIARES
# ======================================================
def conectar_hoja(nombre_hoja):
    creds = service_account.Credentials.from_service_account_info(st.secrets["gcp"])
    client = gspread.authorize(creds)
    return client.open("BD_CONCURSO_ITM").worksheet(nombre_hoja)

def obtener_correos(hoja):
    try:
        return [c.lower().strip() for c in hoja.col_values(1)[1:]]
    except:
        return []

def generar_codigo():
    return str(random.randint(100000, 999999))

def enviar_correo_gmail(service_account_info, destinatario, asunto, mensaje_html):
    st.info(f"📩 Se envió un correo a **{destinatario}** con el código de acceso.")


# ======================================================
# MÓDULO DE LOGIN Y REGISTRO
# ======================================================
def modulo_login():
    st.title("🎓 Bienvenido al Portal del Concurso de Analítica Financiera")

    st.write("Por favor, ingresa tu **correo institucional** para continuar:")
    correo = st.text_input("📧 Correo institucional")

    if not correo:
        st.stop()

    correo = correo.strip().lower()

    # --- Conexiones a hojas ---
    hoja_autorizados = conectar_hoja("correos_autorizados")
    hoja_docentes = conectar_hoja("docentes")
    hoja_estudiantes = conectar_hoja("estudiantes")

    autorizados = obtener_correos(hoja_autorizados)
    docentes = obtener_correos(hoja_docentes)
    estudiantes = obtener_correos(hoja_estudiantes)

    # --- Verificaciones ---
    if correo in docentes or correo in estudiantes:
        st.success("✅ Usuario encontrado. Ingresa para continuar.")

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
                st.session_state["rol"] = "Docente" if correo in docentes else "Estudiante"
                st.success("✅ Acceso concedido correctamente.")
                st.rerun()
            else:
                st.error("❌ Código incorrecto o expirado.")

    else:
        # Usuario no registrado
        st.warning("⚠️ Este correo no se encuentra registrado.")
        st.info("Selecciona tu tipo de registro:")

        rol_seleccionado = st.radio("Rol de registro", ["Estudiante", "Docente"], horizontal=True)

        if rol_seleccionado == "Docente":
            if correo not in autorizados:
                st.error("🚫 Este correo no está autorizado como docente. Contacta al administrador.")
                st.stop()
            else:
                if st.button("Registrar como Docente Autorizado"):
                    hoja_docentes.append_row([correo, "Docente"])
                    st.success("✅ Registro exitoso. Ahora puedes iniciar sesión.")
                    st.rerun()

        elif rol_seleccionado == "Estudiante":
            if st.button("Registrar como Estudiante"):
                hoja_estudiantes.append_row([correo, "Estudiante"])
                st.success("✅ Registro exitoso. Ahora puedes iniciar sesión.")
                st.rerun()

        st.button("Salir", type="secondary")


# ======================================================
# MÓDULOS PRINCIPALES
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


def modulo_inscripcion():
    st.title("📝 Inscripción de participantes")

def modulo_votacion():
    st.title("🗳️ Sistema de votación")

def modulo_resultados():
    st.title("🏆 Resultados del concurso")

def modulo_eventos():
    st.title("📅 Agenda del evento")


# ======================================================
# CONTROL DE ACCESO
# ======================================================
if not st.session_state["usuario_autenticado"]:
    modulo_login()
    st.stop()

# ======================================================
# MENÚ LATERAL (solo visible después de login)
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
