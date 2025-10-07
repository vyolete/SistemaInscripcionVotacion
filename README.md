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

- Opción rápida (usando el archivo requirements.txt del proyecto):
  ```bash
  pip install -r requirements.txt
  ```

- Dependencias principales utilizadas por la app:
  - streamlit, altair, streamlit-option-menu
  - pandas
  - gspread, google-api-python-client, google-auth, google-auth-oauthlib, google-auth-httplib2
  - qrcode[pil], Pillow

Nota: El paquete `sh` está incluido en requirements y puede no ser necesario en producción. Puedes removerlo si no se utiliza.

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

Claves utilizadas por la app:
- `st.secrets["gcp"]`: objeto JSON de credenciales del servicio.
- `st.secrets["spreadsheet"]["id"]`: ID del Google Spreadsheet que contiene las hojas.

### Configuración de Google Sheets (estructuras de hojas)

Para evitar errores, asegúrate de crear las siguientes hojas dentro del mismo Spreadsheet y con las columnas tal como se espera en la aplicación:

- Hoja: `Docentes`
  - Columnas requeridas: `Correo`, `Codigo`
  - Uso: Validación de acceso docente (correo + código).

- Hoja: `Respuestas de formulario 1`
  - Columnas esperadas (según el Google Form vinculado):
    - `Docente`
    - `Inscripción Participantes` (la app lo renombra a `Participantes`)
    - `Id_equipo (Respuestas de formulario 1)` (la app lo renombra a `Id_equipo`)
    - `Nombre del Equipo` (la app lo renombra a `Equipo`)
  - Uso: Base de datos de inscripciones y equipos.

- Hoja: `Votaciones`
  - Encabezados sugeridos para que el módulo de resultados funcione correctamente:
    - `Fecha`
    - `Rol Votante`
    - `Correo`
    - `Id_equipo`
    - `Puntaje_Total`
    - `Criterio 1`
    - `Criterio 2`
    - `Criterio 3`
  - Uso: Registro de votos de docentes y estudiantes/asistentes.

Si cambias los nombres de columnas, deberás ajustar las referencias en `app.py`.

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

Integración con la app:
- La app de Streamlit reconoce el parámetro de la URL `?equipo=<ID>` para facilitar el flujo de votación vía QR.
- Puedes generar QR que apunten a: `https://<tu-dominio-o-localhost>/?equipo=<ID_DEL_EQUIPO>`.
- Si prefieres generar los QR desde Python, el proyecto incluye `qrcode[pil]` y `Pillow` en requirements, aunque la app actual no los usa directamente.

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

### Flujo dentro de la aplicación

- Home: selección de rol (Estudiante o Docente).
- Validación Docente: correo institucional + código (ambos validados contra la hoja `Docentes`).
- Inscripción: acceso directo al Google Form (botón y iframe) para registrar equipos.
- Dashboard: métricas y gráficos por docente y equipo, leyendo únicamente `Respuestas de formulario 1`.
- Votación:
  - Estudiantes/Asistentes: ingresan correo + código del equipo.
  - Docentes: si la sesión es docente, se omite ingresar correo nuevamente.
  - Se impide votar más de una vez por el mismo equipo y correo.
  - Los votos se registran en la hoja `Votaciones` con criterios diferenciados por rol.
- Resultados: cálculo de puntajes ponderados y visualización de Top 3 y Top 20.
- Eventos: sección informativa de próximos eventos.

### Ejecución con Dev Containers (opcional)

Este repositorio incluye `.devcontainer/devcontainer.json` para facilitar el arranque en VS Code/Dev Containers:
- Imagen base: `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`.
- Al adjuntarte al contenedor, se instalan `requirements.txt` y se inicia automáticamente `streamlit run app.py` en el puerto 8501.
- El puerto 8501 se abre como preview en el editor.

Pasos:
1. Abre el repositorio en VS Code.
2. Instala la extensión “Dev Containers”.
3. Reabre en contenedor. El servidor de Streamlit iniciará y podrás ver la preview.

### Estructura del repositorio

```
├── .devcontainer/
│   └── devcontainer.json
├── README.md
├── app.py
└── requirements.txt
```

### Parámetros útiles

- `?equipo=<ID>`: Permite precargar el código de equipo en el módulo de votación (ideal para enlaces QR).

### Solución de problemas (Troubleshooting)

- “Error al cargar la hoja”: verifica que el `spreadsheet.id` en `secrets.toml` sea correcto y que tu servicio tenga permisos de edición/lectura.
- “No hay inscripciones registradas”: revisa que la hoja `Respuestas de formulario 1` exista y tenga columnas esperadas.
- “La columna 'X' no existe”: confirma nombres exactos de columnas o ajusta la lógica de renombrado en `app.py`.
- “Ya votaste por este equipo”: el sistema evita duplicidad de votos por combinación `Correo` + `Id_equipo`.
- Preview/puerto 8501 no abre: si usas Dev Containers, espera la instalación inicial o abre manualmente con `streamlit run app.py`.

### Roadmap sugerido

- Administración: panel para gestión de docentes, equipos y votaciones desde la app.
- Exportación: descarga de reportes en CSV/Excel desde el dashboard.
- Seguridad: validaciones adicionales y auditoría de cambios.
- Notificaciones: integración directa desde Python para emails (si no se usa Apps Script).

### Contribución

1. Haz un fork del repositorio.
2. Crea una rama para tu feature o fix: `git checkout -b feature/mi-mejora`.
3. Realiza tus cambios y pruebas.
4. Abre un Pull Request describiendo la mejora y el impacto.

### Estado del proyecto

- La aplicación Streamlit incluida (`app.py`) contiene módulos de Home, Inscripción, Dashboard, Votación, Resultados y Eventos.
- La integración depende de la correcta configuración de `st.secrets` y de las tres hojas de cálculo (`Docentes`, `Respuestas de formulario 1`, `Votaciones`).
- Algunas dependencias (ej. `qrcode`) están disponibles para futuras extensiones, aunque no se usan actualmente en `app.py`.

---

## Licencia

MIT License

---

## Créditos

Desarrollado por [vyolete](https://github.com/vyolete) para la Institución Universitaria ITM.  
Inspirado en la mejora de procesos académicos y eventos universitarios.

---

