import streamlit as st
import pandas as pd
import gspread
import random
import string
import base64
from google.oauth2.service_account import Credentials
from email.mime.text import MIMEText
from googleapiclient.discovery import build

# ======================================================
# 🔹 CONFIGURACIÓN GOOGLE SHEETS
# ======================================================
def cargar_hoja(nombre_hoja):
    alcances = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    credenciales = Credentials.from_service_account_info(st.secrets["gcp"], scopes=alcances)
    cliente = gspread.authorize(credenciales)
    hoja = cliente.open("Concurso Analítica Financiera").worksheet(nombre_hoja)
    return hoja

# ======================================================
# 🔹 FUNCIÓN PARA ENVIAR CORREOS GMAIL
# ======================================================
def enviar_correo_gmail(destinatario, asunto, mensaje_html):
    try:
        credenciales = Credentials.from_service_account_info(
            st.secrets["gcp"], scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        servicio = build('gmail', 'v1', credentials=credenciales)

        mensaje = MIMEText(mensaje_html, "html")
        mensaje["to"] = destinatario
        mensaje["subject"] = asunto

        mensaje_raw = {"raw": base64.urlsafe_b64encode(mensaje.as_bytes()).decode()}
        servicio.users().messages().send(userId="me", body=mensaje_raw).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")
        return False

# ======================================================
# 🔹 FUNCIÓN PARA GENERAR CONTRASEÑAS ALEATORIAS
# ======================================================
def generar_contrasena(longitud=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=longitud))

# ======================================================
# 🔹 LOGIN Y REGISTRO GENERAL (DOCENTES / ESTUDIANTES)
# ======================================================
def login_general():
    st.title("🔐 Acceso al Sistema")

    rol = st.selectbox("Seleccione su rol:", ["Docente", "Estudiante"])
    hoja = cargar_hoja("Docentes" if rol == "Docente" else "Estudiantes")
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if "correo_usuario" not in st.session_state:
        st.session_state["correo_usuario"] = None
        st.session_state["rol_usuario"] = None

    opcion = st.radio("Seleccione una opción:", ["Iniciar sesión", "Registrarse"])

    # === LOGIN ===
    if opcion == "Iniciar sesión":
        correo = st.text_input("Correo institucional:")
        contrasena = st.text_input("Contraseña:", type="password")

        if st.button("Iniciar sesión"):
            if not correo or not contrasena:
                st.warning("⚠️ Por favor ingrese sus credenciales completas.")
            else:
                usuario = df[(df["Correo"] == correo) & (df["Contraseña"] == contrasena)]
                if not usuario.empty:
                    st.session_state["correo_usuario"] = correo
                    st.session_state["rol_usuario"] = rol
                    st.success(f"✅ Bienvenido/a {usuario.iloc[0]['Nombre']} ({rol})")
                else:
                    st.error("❌ Credenciales incorrectas o usuario no registrado.")

    # === REGISTRO ===
    elif opcion == "Registrarse":
        nombre = st.text_input("Nombre completo:")
        correo = st.text_input("Correo institucional:")
        institucion = st.text_input("Institución:")

        if st.button("Registrar"):
            if not nombre or not correo or not institucion:
                st.warning("⚠️ Complete todos los campos.")
            elif correo in df["Correo"].values:
                st.info("ℹ️ Este correo ya está registrado.")
            else:
                contrasena = generar_contrasena()
                hoja.append_row([nombre, correo, institucion, contrasena])

                mensaje = f"""
                <h3>📘 Bienvenido al Concurso Analítica Financiera</h3>
                <p>Hola <b>{nombre}</b>, tu registro fue exitoso como <b>{rol}</b>.</p>
                <p>Tu contraseña temporal es: <b>{contrasena}</b></p>
                <p>Por favor inicia sesión en el sistema para completar tus datos.</p>
                """

                if enviar_correo_gmail(correo, f"Registro exitoso - Concurso ITM ({rol})", mensaje):
                    st.success("✅ Registro completado. Se envió la contraseña a tu correo.")
                else:
                    st.warning("Registro completado, pero no se pudo enviar el correo.")

# ======================================================
# 🔹 PANEL DOCENTE
# ======================================================
def panel_docente():
    st.subheader("📘 Panel Docente")
    st.write("Aquí irán las funciones para docentes: inscripción de proyectos, evaluación, etc.")
    if st.button("Cerrar sesión"):
        st.session_state["correo_usuario"] = None
        st.session_state["rol_usuario"] = None
        st.rerun()

# ======================================================
# 🔹 PANEL ESTUDIANTE
# ======================================================
def panel_estudiante():
    st.subheader("🎓 Panel Estudiante")
    st.write("Aquí irán las funciones para estudiantes: ver su equipo, resultados, etc.")
    if st.button("Cerrar sesión"):
        st.session_state["correo_usuario"] = None
        st.session_state["rol_usuario"] = None
        st.rerun()

# ======================================================
# 🔹 INTERFAZ PRINCIPAL
# ======================================================
def main():
    st.sidebar.title("🏆 Concurso Analítica Financiera")
    menu = st.sidebar.radio("Menú principal", ["Inicio", "Login", "Panel"])

    if menu == "Inicio":
        st.markdown("""
        # 🎯 Bienvenido al Concurso Analítica Financiera ITM
        Selecciona **Login** para ingresar como Docente o Estudiante.
        """)

    elif menu == "Login":
        login_general()

    elif menu == "Panel":
        if st.session_state.get("correo_usuario"):
            rol = st.session_state.get("rol_usuario")
            st.success(f"Sesión activa: {st.session_state['correo_usuario']} ({rol})")
            if rol == "Docente":
                panel_docente()
            elif rol == "Estudiante":
                panel_estudiante()
        else:
            st.warning("🔒 Debes iniciar sesión primero desde el menú *Login*.")

# ======================================================
# 🔹 EJECUCIÓN
# ======================================================
if __name__ == "__main__":
    main()
