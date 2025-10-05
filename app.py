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
       @media (max-width: 768px) {
       /* Mostrar un aviso flotante al seleccionar Estudiante */
       .menu-flotante {
           position: fixed;
           bottom: 20px;
           right: 20px;
           background-color: #1B396A;
           color: white;
           font-weight: 600;
           padding: 12px 18px;
           border-radius: 30px;
           box-shadow: 0 2px 10px rgba(0,0,0,0.2);
           z-index: 9999;
           animation: fadeIn 0.5s ease-in-out;
       }
       @keyframes fadeIn {
           from {opacity: 0;}
           to {opacity: 1;}
       }
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


           # ================================================================
           # === FUNCIONES AUXILIARES ===
           # ================================================================

   def cargar_hoja(nombre_hoja):
       creds = Credentials.from_service_account_info(st.secrets["gcp"])
       client = gspread.authorize(creds)
       sheet_id = st.secrets["spreadsheet"]["id"]
       sheet = client.open_by_key(sheet_id)
       worksheet = sheet.worksheet(nombre_hoja)
       data = worksheet.get_all_records()
       return pd.DataFrame(data)

   def guardar_fila(nombre_hoja, fila):
       creds = Credentials.from_service_account_info(st.secrets["gcp"])
       client = gspread.authorize(creds)
       sheet_id = st.secrets["spreadsheet"]["id"]
       sheet = client.open_by_key(sheet_id)
       worksheet = sheet.worksheet(nombre_hoja)
       worksheet.append_row(fila)



   def generar_codigo_docente():
       """Genera un código aleatorio tipo DOC-XXXX."""
       codigo = "DOC-" + ''.join(random.choices(string.digits, k=4))
       return codigo


   def enviar_correo_gmail(service_account_info, destinatario, asunto, mensaje_html):
       """Envía un correo usando Gmail API con la cuenta concursos.itm@gmail.com"""
       try:
           credentials = service_account.Credentials.from_service_account_info(
               service_account_info,
               scopes=["https://www.googleapis.com/auth/gmail.send"]
           )
           delegated = credentials.with_subject(st.secrets["gmail"]["user"])
           service = build("gmail", "v1", credentials=delegated)

           mime_message = MIMEText(mensaje_html, "html")
           mime_message["to"] = destinatario
           mime_message["from"] = st.secrets["gmail"]["user"]
           mime_message["subject"] = asunto

           encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
           create_message = {"raw": encoded_message}

           service.users().messages().send(userId="me", body=create_message).execute()
           return True
       except Exception as e:
           st.error(f"⚠️ Error al enviar correo: {e}")
           return False


   # ================================================================
   # === MÓDULO PRINCIPAL HOME ===
   # ================================================================

   def modulo_home():
       st.title("🏫 Portal del Concurso ITM")

       # Inicializar variables de sesión
       if "usuario_autenticado" not in st.session_state:
           st.session_state["usuario_autenticado"] = False

       # =====================================================
       # ======= LOGIN / REGISTRO DE DOCENTES ================
       # =====================================================
       def modulo_login():
           st.header("🔐 Acceso al sistema")

           correo = st.text_input("Correo institucional")
           codigo = st.text_input("Código de acceso", type="password")

           col1, col2, col3 = st.columns(3)
           with col1:
               login = st.button("Iniciar sesión")
           with col2:
               nuevo = st.button("Usuario nuevo")
           with col3:
               olvidar = st.button("Olvidé mi código")

           if login:
               if not correo or not codigo:
                   st.warning("Por favor completa ambos campos.")
                   return

               df_doc = cargar_hoja("Docentes")
               df_aut = cargar_hoja("Correos Autorizados")

               # Validar si el correo está autorizado
               if correo not in df_aut["Correo"].values:
                   st.error("❌ Este correo no está autorizado para registrarse como docente.")
                   return

               # Validar si está registrado
               fila_docente = df_doc[df_doc["Correo institucional"] == correo]
               if fila_docente.empty:
                   st.warning("⚠️ Este correo aún no está registrado. Regístrate primero.")
               else:
                   codigo_guardado = fila_docente.iloc[0]["Código acceso"]
                   if codigo.strip() == str(codigo_guardado).strip():
                       st.success(f"✅ Bienvenido {fila_docente.iloc[0]['Nombre']}")
                       st.session_state["usuario"] = correo
                       st.session_state["rol"] = "Docente"
                   else:
                       st.error("❌ Código incorrecto.")

           elif nuevo:
               df_aut = cargar_hoja("Correos Autorizados")
               if correo not in df_aut["Correo"].values:
                   st.error("❌ Este correo no está autorizado para registrarse como docente.")
                   return

               df_doc = cargar_hoja("Docentes")
               if correo in df_doc["Correo institucional"].values:
                   st.info("✅ Ya estás registrado. Inicia sesión con tu código.")
                   return

               nombre = st.text_input("Nombre completo")
               facultad = st.selectbox("Facultad", ["Ciencias Económicas", "Otra (futura)"])
               if st.button("Registrar docente"):
                   codigo = "DOC-" + ''.join(random.choices(string.digits, k=4))
                   timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                   fila = [timestamp, nombre, correo, facultad, codigo, "Docente", "Activo"]
                   guardar_fila("Docentes", fila)

                   mensaje_html = f"""
                   <h3>👋 Hola {nombre}</h3>
                   <p>Tu registro como <b>docente</b> en el sistema ITM ha sido exitoso.</p>
                   <p>Tu código de acceso es: <b>{codigo}</b></p>
                   <p>Guarda este código, lo necesitarás para ingresar.</p>
                   """
                   enviar_correo(correo, "Código de acceso ITM", mensaje_html)
                   st.success("✅ Registrado correctamente. Revisa tu correo para obtener tu código.")

           elif olvidar:
               if not correo:
                   st.warning("Por favor ingresa tu correo institucional.")
                   return
               df_doc = cargar_hoja("Docentes")
               fila_docente = df_doc[df_doc["Correo institucional"] == correo]
               if fila_docente.empty:
                   st.error("No encontramos tu registro como docente.")
               else:
                   codigo_guardado = fila_docente.iloc[0]["Código acceso"]
                   mensaje_html = f"""
                   <h3>🔑 Recuperación de código</h3>
                   <p>Tu código de acceso es: <b>{codigo_guardado}</b></p>
                   """
                   enviar_correo(correo, "Recuperación de código ITM", mensaje_html)
                   st.success("📩 Código enviado nuevamente a tu correo institucional.")

       # =====================================================
       # ======= MENÚ PRINCIPAL DESPUÉS DE LOGIN =============
       # =====================================================
       correo_actual = st.session_state.get("correo_actual", "")
       rol = st.session_state.get("rol", "Invitado")

       st.markdown(f"👋 Bienvenido **{correo_actual}** — Rol: **{rol}**")

       if st.button("🚪 Cerrar sesión"):
           st.session_state.clear()
           st.rerun()

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

       # === 🔹 Leer parámetros de la URL (QR o manual) ===
       params = st.query_params
       equipo_qr = params.get("equipo", [None])[0] if "equipo" in params else None
       rol_qr = params.get("rol", [None])[0] if "rol" in params else None

       # Mostrar mensaje si viene desde QR
       if equipo_qr:
           st.info(f"📲 Ingreso directo: estás votando por el equipo **{equipo_qr}**")

       # Control de sesión
       if "validado_voto" not in st.session_state:
           st.session_state.validado_voto = False

       # === 🔹 Paso 1: Validación de rol y datos ===
       if not st.session_state.validado_voto:
           # Rol automático si viene del QR, sino seleccionable
           rol = (
               "Docente" if rol_qr == "docente"
               else "Estudiante / Asistente" if rol_qr == "estudiante"
               else st.radio("Selecciona tu rol:", ["Estudiante / Asistente", "Docente"], horizontal=True)
           )

           # Datos del formulario
           correo = st.text_input("📧 Correo institucional:")
           equipo_id = st.text_input(
               "🏷️ Código del equipo a evaluar:",
               value=equipo_qr or "",
               disabled=bool(equipo_qr)  # 🔒 Bloquear si viene desde QR
           )

           if st.button("Continuar ▶️"):
               if not correo or not equipo_id:
                   st.error("❌ Debes ingresar tu correo y el código del equipo.")
                   return
               try:
                   df_insc = preparar_dataframe(conectar_google_sheets(st.secrets))
                   if equipo_id not in df_insc["ID Equipo"].astype(str).tolist():
                       st.error("❌ El código del equipo no existe.")
                       return

                   # Validación de docentes
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

       # === 🔹 Paso 2: Formulario de votación ===
       else:
           rol = st.session_state.rol_voto
           correo = st.session_state.correo_voto
           equipo_id = st.session_state.equipo_voto

           # Mostrar cabecera con animación
           st.markdown("""
               <style>
               @keyframes fadeIn {
                   from {opacity: 0; transform: translateY(10px);}
                   to {opacity: 1; transform: translateY(0);}
               }
               .titulo-voto {
                   animation: fadeIn 1s ease-out;
                   color: #1B396A;
                   font-size: 20px;
                   font-weight: bold;
                   text-align: center;
                   margin-bottom: 15px;
               }
               </style>
           """, unsafe_allow_html=True)

           st.markdown(f"<div class='titulo-voto'>📋 Evaluación del Proyecto ({rol})</div>", unsafe_allow_html=True)

           # === 🔸 Consultar si ya votó ===
           try:
               credentials = service_account.Credentials.from_service_account_info(
                   st.secrets["gcp"], scopes=["https://www.googleapis.com/auth/spreadsheets"]
               )
               gc = gspread.authorize(credentials)
               sh = gc.open_by_key(st.secrets["spreadsheet"]["id"])
               ws_votos = sh.worksheet("Votaciones")

               votos = pd.DataFrame(ws_votos.get_all_records())
               ya_voto = False
               if not votos.empty:
                   ya_voto = not votos[(votos["Correo"] == correo) & (votos["ID Equipo"] == equipo_id)].empty

               # === 🔸 Si ya votó ===
               if ya_voto:
                   st.warning(f"⚠️ Ya registraste un voto para el equipo **{equipo_id}**.")
                   st.markdown("<br>", unsafe_allow_html=True)
                   if st.button("🔄 Votar por otro equipo"):
                       st.session_state.validado_voto = False
                       if "equipo_voto" in st.session_state:
                           del st.session_state["equipo_voto"]
                       st.rerun()
                   return

           except Exception as e:
               st.error(f"⚠️ Error al cargar datos de votaciones: {e}")
               return

           # === 🔸 Si aún puede votar ===
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

           st.markdown(f"<div style='margin-top:10px; color:#1B396A;'>🧮 Puntaje total: <b>{puntaje_total}</b></div>", unsafe_allow_html=True)

           if st.button("✅ Enviar voto"):
               try:
                   registro = [str(datetime.now()), rol, correo, equipo_id, puntaje_total]
                   ws_votos.append_row(registro)
                   st.success("✅ ¡Tu voto ha sido registrado exitosamente!")
                   st.balloons()

                   if st.button("🔄 Votar por otro equipo"):
                       st.session_state.validado_voto = False
                       if "equipo_voto" in st.session_state:
                           del st.session_state["equipo_voto"]
                       st.rerun()
               except Exception as e:
                   st.error(f"⚠️ Error al registrar el voto: {e}")

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
               # Usa el path completo del archivo subido
               st.image("data:image/jpeg;base64,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", use_container_width=True)
           except Exception:
               # En caso de error, mostrar un mensaje y un placeholder
               st.warning("⚠️ No se pudo cargar la imagen del conferencista.")
               st.image("https://media1.giphy.com/media/ZBoap6UCvOEeQNGzHK/200.webp", use_container_width=True)

       with col2:
           st.markdown("""
           <div style="color:#1B396A; font-family:'Segoe UI', sans-serif;">
               <h3 style="margin-bottom:0;">🎙️ Conferencista: <b>Carlos Naranjo</b></h3>
               <p style="font-size:15px; text-align:justify;">
                   Magíster en Gestión de Organizaciones, especialista en Gerencia para Ingenieros del ITM e Ingeniero Informático.
                   Como Gerente de Monitoreo de Canales, ha liderado la integración de tecnologías e inteligencia artificial
                   en procesos financieros, demostrando cómo la innovación puede transformar los retos en oportunidades.
                   Su propósito es inspirar a las nuevas generaciones a aprovechar la tecnología como motor de cambio y crecimiento.
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
