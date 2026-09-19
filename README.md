# 🏫 Teacher Duty Scheduler (GuardPlan)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-18+-DD0031?style=flat-square&logo=angular&logoColor=white)](https://angular.dev/)
[![OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> **Sistema inteligente de planificación y optimización combinatoria de guardias docentes para centros educativos.**

---

## 📌 Descripción del Proyecto

En los centros de educación secundaria y primaria, la asignación de guardias lectivas semanales suele ser un proceso manual propenso a desbalances, fatiga de personal y errores humanos ante bajas médicas de última hora.

**Teacher Duty Scheduler** resuelve este problema formulándolo como un modelo matemático de **Programación con Restricciones (Constraint Programming / CP-SAT)** a través de **Google OR-Tools**. La plataforma desacopla el horario lectivo base (fijo durante el curso escolar) de las ausencias imprevistas por fechas de calendario reales, garantizando un reparto equitativo de carga lectiva y cobertura óptima.

---

## ✨ Características Principales

- **Optimización Matemática Robusta (CP-SAT)**:
  - **Restricciones Duras (Hard Constraints)**: Respeto inquebrantable a clases lectivas (`TEACHING`), permisos/bajas médicas puntuales (`ABSENCE`) y no duplicidad de un docente en el mismo periodo.
  - **Restricciones Blandas (Soft Constraints)**: Minimización de la brecha de guardias entre docentes (equidad/varianza mínima) y penalización de horas consecutivas (anti-fatiga).
  - **Tolerancia a Déficit (Subcobertura Controlada)**: Variables de holgura que permiten resolver el cuadrante sin fallar cuando hay menos profesores libres que los 2 requeridos por bloque, generando alertas formales.
- **Gestión de Claustro y Departamentos**:
  - Identificación por GUID (UUID v4) automático.
  - Catalogación por departamentos didácticos (Matemáticas, Lengua, Ciencias, etc.).
- **Calendario Real**:
  - Proyección de semanas ancladas a fechas ISO (`YYYY-MM-DD`).
  - Navegador quincenal y semanal directo (adelantar/retrasar 7 días).
- **Persistencia Ligera**: SQLite gestionado con **SQLModel / SQLAlchemy** en un único fichero local (`guardias.db`).
- **Arquitectura Limpia (Clean Architecture)**:
  - Dominio puro desacoplado de frameworks.
  - Casos de uso e interfaces con inversión de dependencias.
  - Frontend modular con Angular Standalone Components y CSS encapsulado.
- **Despliegue Rápido**: Preparado para producción local mediante **Docker Compose** y Nginx.

---

## 🛠️ Stack Tecnológico

### Backend
- **Lenguaje**: Python 3.11+
- **Framework API**: FastAPI + Uvicorn
- **Motor de Optimización**: Google OR-Tools (`cp_model`)
- **ORM / Persistencia**: SQLModel + SQLite
- **Exportación**: OpenPyXL (Excel)

### Frontend
- **Framework**: Angular 18+ (Standalone Components, Inyección de dependencias moderna con `inject()`)
- **Estilos**: CSS Vanilla con variables y responsive design (Flexbox/Grid)
- **Servidor Web Producción**: Nginx Alpine

---

## 📂 Estructura del Repositorio

```text
teacher-duty-scheduler/
├── docker-compose.yml              # Orquestador multi-contenedor
├── Backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── seed_demo.py               # Generador de datos y casos de prueba
│   └── src/
│       ├── domain/                # Entidades y constantes de negocio puras
│       ├── services/              # Motor CP-SAT y caso de uso orquestador
│       ├── infrastructure/        # Modelos SQLModel, repositorios y exporters
│       ├── api/                   # Controladores FastAPI, esquemas e inyección
│       └── main.py                # Punto de entrada de la API
└── Frontend/
    ├── Dockerfile                 # Multi-stage build (Node -> Nginx)
    ├── nginx.conf                 # Proxy inverso y servidor estático
    └── src/app/
        ├── models/                # Interfaces TypeScript
        ├── services/              # Clientes HTTP
        └── features/              # Componentes funcionales (teachers, absences, guards)
