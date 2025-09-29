# Sistema de Inscripción y Votación para Concurso Académico ITM

Este sistema facilita la **inscripción de equipos**, la **gestión de votaciones** y la **visualización de resultados** en concursos académicos, con un enfoque en eventos universitarios como el Concurso de Analítica Financiera ITM. La solución integra una aplicación web basada en Streamlit y automatizaciones mediante Google Sheets y Google Apps Script.

---

## Tabla de Contenidos

- [Características Principales](#características-principales)
- [Arquitectura General](#arquitectura-general)
- [Instalación y Configuración](#instalación-y-configuración)
- [Automatizaciones (Google Apps Script)](#automatizaciones-google-apps-script)
- [Personalización y Experiencia de Usuario](#personalización-y-experiencia-de-usuario)
- [Uso](#uso)
- [Licencia](#licencia)
- [Créditos](#créditos)

---

## Características Principales

- **Inscripción de equipos** a través de un formulario web (Google Forms) conectado automáticamente a Google Sheets.
- **Asignación automática de códigos únicos** a cada equipo inscrito.
- **Notificaciones automáticas** por correo electrónico a participantes y docentes, incluyendo detalles de inscripción y un código QR personalizado para la votación.
- **Votación diferenciada** para docentes y asistentes/estudiantes, con validación de identidad y control de duplicidad.
- **Dashboard en tiempo real** con métricas de inscripción y votación, filtrado por docente o equipo.
- **Integración completa con Google Sheets** para la gestión de datos y automatización de procesos administrativos.

---

## Arquitectura General

```
Usuario
   │
   ▼
[Streamlit App]  ←→  [Google Sheets]  ←→  [Google Apps Script]
   │                  │                     ▲
   └──> Formularios   └──> Datos             └──> Correos/QRs/Automatización
```

- **Frontend:** Streamlit (Python)
- **Backend:** Google Sheets + Google Apps Script (Javascript)
- **Notificaciones:** Envío de correos desde Apps Script

---

## Instalación y Configuración

### Requisitos

- Python 3.8 o superior
- Cuenta de Google Cloud con credenciales de servicio para acceso a Google Sheets
- Google Sheets configurado con hojas:
  - Inscripciones (Sheet1)
  - Docentes
  - Votaciones

### Instalación de dependencias

```bash
pip install streamlit gspread pandas google-auth
```

### Configuración de credenciales en Streamlit

Crea el archivo `.streamlit/secrets.toml` con tus credenciales de Google y el ID del Spreadsheet:

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

## Automatizaciones (Google Apps Script)

Se utiliza un script en Google Apps Script vinculado a la hoja de inscripciones para:

- **Normalizar datos** (evitar errores por tildes y mayúsculas).
- **Asignar automáticamente un código único** a cada equipo.
- **Generar enlaces de votación y códigos QR** personalizados.
- **Enviar confirmaciones automáticas** por correo electrónico con todos los detalles y recursos necesarios para la participación y votación.

**Fragmento del script principal:**

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
  // Lógica para leer la inscripción, asignar código, generar QR y enviar correo
  // ...
}
```
> El script completo está disponible en el repositorio.

---

## Personalización y Experiencia de Usuario

- **Interfaz visual personalizada** con identidad institucional (colores, logos, mensajes).
- **Mensajes adaptados** al rol del usuario (docente o estudiante/asistente).
- **Notificaciones automáticas** con detalles y QR personalizado.
- **Flujo de navegación claro**, con menú lateral y validaciones de acceso.

---

## Uso

1. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```
2. Accede a la URL local proporcionada.
3. Navega según tu rol (docente o estudiante), realiza inscripciones y participa en la votación.

---

## Licencia

MIT License

---

## Créditos

Desarrollado por [vyolete](https://github.com/vyolete) para la Institución Universitaria ITM.  
Inspirado en la mejora de procesos académicos y eventos universitarios.

---

