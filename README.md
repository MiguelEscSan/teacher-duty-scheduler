# 📚 Teacher Duty Scheduler

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> Sistema inteligente y automatizado para la asignación y planificación equitativa de guardias docentes en centros educativos.

---

## 📖 Descripción

**Teacher Duty Scheduler** es una herramienta diseñada para centros escolares e institutos que simplifica la compleja tarea de organizar las guardias del profesorado (patios, pasillos, biblioteca, sustituciones en aula, etc.). 

A través de un algoritmo de asignación con restricciones, el sistema distribuye los turnos de manera equilibrada y justa, respetando los horarios lectivos, preferencias, descansos y limitaciones de cada docente.

---

## ✨ Características principales

- **⚖️ Reparto Equitativo:** Algoritmo optimizado para balancear el número de guardias semanales/mensuales entre todo el claustro.
- **🚫 Resolución de Conflictos y Restricciones:**
  - Evita solapamientos con horas lectivas de clase.
  - Respeta reducciones de jornada, cargos directivos o días libres.
  - Límites máximos y mínimos de guardias por profesor y periodo.
- **📍 Multizona / Múltiples Puntos de Guardia:** Gestión de distintos puestos (patio infantil, patio primaria, biblioteca, cafetería, accesos, etc.).
- **📅 Visualización de Cuadrantes:** Generación de horarios visuales por docente, por día y por zona.
- **📊 Exportación e Informes:** Capacidad de exportar los cuadrantes a formatos estándar (Excel/CSV, PDF, etc.).
- **🔄 Gestión de Sustituciones y Modificaciones:** Registro dinámico de cambios puntuales o bajas de última hora.

---

## 🛠️ Tecnologías

- **Backend / Algoritmo:** Python 
- **Frontend :** Interfaz Web (Angular)
- **Base de Datos / Almacenamiento:** SQLite 
- **Aplicación de escritorio:** PyInstaller + pywebview (WebView2 de Windows)

---

## 🚀 Instalación y Puesta en Marcha

### Prerrequisitos

- [Git](https://git-scm.com/) instalado.
- Entorno de ejecución según corresponda:
  - **Python 3.10+** (si es un proyecto Python)
  - **Node.js 18+** (si es un proyecto JavaScript/TypeScript)

### 1. Clonar el repositorio

```bash
git clone https://github.com/MiguelEscSan/teacher-duty-scheduler.git
cd teacher-duty-scheduler
```

---

## 🖥️ Aplicación de escritorio (Windows `.exe`)

La aplicación se puede distribuir como un único `Guardias.exe` que no necesita tener Python ni Node instalados: al abrirlo arranca el backend internamente y muestra la interfaz en una ventana propia.

### Ejecutar el `.exe`

1. Haz doble clic en `Guardias.exe`.
2. Se abre la ventana **Gestor de Guardias** (tarda un par de segundos la primera vez). Al cerrarla, la aplicación se detiene.

Los datos se guardan fuera del ejecutable, en `%APPDATA%\Guardias\`:

| Archivo | Contenido |
|---|---|
| `guardias.db` | Base de datos SQLite. Se conserva al actualizar o recompilar el `.exe`. |
| `guardias.log` | Registro de errores, útil si la aplicación no arranca. |
| `.env` | *(Opcional)* Configuración SMTP para el envío de correos. |

La forma recomendada es configurarlo desde la app, en **Ajustes de correo**: correo de la cuenta (que también es el remitente), contraseña de aplicación, plantilla del mensaje y un envío de prueba. El servidor SMTP lo fija la aplicación (`smtp.gmail.com`, puerto 587 con STARTTLS o 465 con SSL). La contraseña se guarda cifrada en la base de datos (la clave de cifrado está en `secret.key`, junto a `guardias.db`).

Si no hay configuración guardada en la app, se usan las variables de [`.env.example`](.env.example) (útil con Docker). Para ese modo, crea un `.env` en `%APPDATA%\Guardias\` (o junto al `.exe`), sin la línea `DB_DIR`. Sin configuración la aplicación funciona igual; solo fallará el envío de notificaciones.

> Al no estar firmado digitalmente, Windows SmartScreen puede mostrar un aviso la primera vez: pulsa **Más información → Ejecutar de todas formas**.

### Generar el `.exe`

Requisitos: **Python 3.10+** y **Node.js 18+**. Desde la raíz del proyecto, con el `.exe` cerrado:

```bash
powershell -ExecutionPolicy Bypass -File build.ps1
```

El script compila el frontend de Angular, instala en `Backend\.venv` las dependencias de empaquetado ([`requirements-desktop.txt`](Backend/requirements-desktop.txt)) y genera **`Backend\dist\Guardias.exe`**.

### Cómo está montado

- **[`Backend/desktop.py`](Backend/desktop.py)**: punto de entrada del `.exe`. Arranca FastAPI con uvicorn en segundo plano (puerto `8765`, u otro libre si está ocupado) y abre la interfaz con [pywebview](https://pywebview.flowrl.com/), que usa el WebView2 ya incluido en Windows. Se eligió en lugar de Electron porque no obliga a empaquetar Node ni Chromium (el `.exe` ronda los 70 MB).
- **[`Backend/src/main.py`](Backend/src/main.py)**: si existe el build de Angular, FastAPI sirve también el frontend, de modo que interfaz y API comparten origen (`/api/v1`). En desarrollo con `ng serve` y en Docker el comportamiento no cambia.
- **[`Backend/guardias.spec`](Backend/guardias.spec)**: configuración de PyInstaller. Incluye el build de Angular, las librerías nativas de OR-Tools y el icono [`Backend/assets/icon.ico`](Backend/assets/icon.ico).
- **[`build.ps1`](build.ps1)**: automatiza todo el proceso de compilación.
