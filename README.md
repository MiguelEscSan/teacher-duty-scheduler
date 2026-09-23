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

---

## 🚀 Instalación y Puesta en Marcha

### Prerrequisitos

- [Git](https://git-scm.com/) instalado.
- Entorno de ejecución según corresponda:
  - **Python 3.10+** (si es un proyecto Python)
  - **Node.js 18+** (si es un proyecto JavaScript/TypeScript)

### 1. Clonar el repositorio

```bash
git clone [https://github.com/MiguelEscSan/teacher-duty-scheduler.git](https://github.com/MiguelEscSan/teacher-duty-scheduler.git)
cd teacher-duty-scheduler
