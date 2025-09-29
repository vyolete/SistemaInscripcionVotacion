# 🏆 Concurso Analítica Financiera ITM

Sistema web para la inscripción, votación y visualización de resultados del Concurso de Analítica Financiera del ITM. Incluye automatizaciones y personalización para una experiencia fluida, segura y personalizada, integrando Google Sheets, generación de códigos automáticos y confirmaciones inteligentes.

---

## 🚀 Características

- **Inscripción de equipos**  
  Formulario integrado vía Google Forms. Al inscribirse, se automatiza:
  - Asignación de un código único de participación a cada equipo.
  - Generación automática de un enlace personalizado para la votación de cada equipo.
  - Creación de un QR único para facilitar la votación mediante escaneo.
  - Envío automático de un correo de confirmación personalizado tanto al estudiante líder como al docente, incluyendo el QR y el enlace directo.
  - Personalización del correo con datos específicos del equipo, participantes y docente.
  - Validación y normalización de nombres para evitar errores de acentos y mayúsculas/minúsculas.

- **Dashboard**  
  Visualización en tiempo real de inscripciones, métricas principales y resumen por docente, todo sincronizado con Google Sheets.

- **Votación segura y adaptativa**  
  - Votación diferenciada para docentes y asistentes/estudiantes.
  - Validación de votantes por correo institucional.
  - Verificación automática para evitar votos duplicados.
  - Filtrado y visualización de votos y resultados en tiempo real.

- **Personalización y experiencia ITM**  
  - Interfaz personalizada con los colores, logos y mensajes del ITM.
  - Mensajes motivacionales y avisos contextuales.
  - Menú y flujo de navegación adaptado según el rol (docente o estudiante/asistente).

---

## ⚙️ Automatizaciones y Scripts

### Google Apps Script para automatización (fragmento esencial):

```javascript
function normalize(str) {
  if (!str) return "";
  return str
    .toString()
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, ""); 
}

function enviarConfirmacion(e) {
  // ... (ver código completo en el repositorio)
  // 1. Obtiene los datos de la fila de inscripción.
  // 2. Normaliza los nombres para emparejar correctamente docentes.
  // 3. Busca el correo del docente asignado.
  // 4. Genera un código único automático para el equipo (ej: ITM2025-001).
  // 5. Crea un enlace a la votación y un QR personalizado.
  // 6. Arma un correo HTML personalizado con toda la información y el QR.
  // 7. Envía el correo al estudiante líder y al docente.
}
```

- **Automatización:**  
  Cada vez que se recibe una inscripción, el script asigna y almacena el código, genera el QR y envía los correos automáticamente, sin intervención manual.
- **Personalización:**  
  El correo incluye los nombres y datos del equipo, docente, código y QR únicos.

---

## 🏗️ Estructura del Proyecto

- `app.py`: App principal desarrollada en Streamlit.
- Google Sheets:  
  - Hoja de inscripciones (usada por el dashboard y votación).
  - Hoja de docentes (validación de jurados).
  - Hoja de votaciones (registro de votos).
- Apps Script: Automatización de confirmaciones y generación de códigos.

---

## 📦 Instalación y Configuración

### 1. Requisitos

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [gspread](https://github.com/burnash/gspread)
- [pandas](https://pandas.pydata.org/)
- [google-auth](https://google-auth.readthedocs.io/)
- Google Cloud Service Account con acceso a Sheets.
- Google Apps Script para automatización en la hoja de cálculo.

Instala las dependencias:
```bash
pip install streamlit gspread pandas google-auth
```

### 2. Configura los secretos

Coloca los datos de tu cuenta de servicio en `.streamlit/secrets.toml`:

```toml
[gcp]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
...
[spreadsheet]
id = "TU_SPREADSHEET_ID"
```

---

## ▶️ Ejecución

```bash
streamlit run app.py
```

Abre la URL local que se muestra en la terminal.

---

## 📝 Notas Importantes

- **Automatización:** El sistema de inscripción, generación de códigos, enlaces y QRs, así como el envío de correos, es 100% automático vía Google Apps Script.
- **Personalización completa:** Desde la interfaz visual hasta los mensajes y correos, todo está adaptado al branding y cultura ITM.
- **Código de ejemplo y Apps Script:** Consulta el repositorio para ver el script completo de automatización.

---

## 👨‍💻 Autor

- [vyolete](https://github.com/vyolete)

---

## 📄 Licencia

MIT License

---

¡Participa, aprende y vive la experiencia del Concurso Analítica Financiera ITM! 🚀
