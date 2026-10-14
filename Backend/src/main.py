"""
Punto de entrada de la aplicación FastAPI.
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse

from src.api.routes import absences, guards, groups, schedules, substitutions, teachers
from src.infrastructure.db.config import init_db
from src.domain.exceptions.assignment_exceptions import (
    ConflictException,
    EntityNotFoundException,
)
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Gestor de Guardias y Claustro",
    version="2.0.0",
    lifespan=lifespan,
)


@app.exception_handler(ConflictException)
async def conflict_exception_handler(request: Request, exc: ConflictException):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(EntityNotFoundException)
async def entity_not_found_exception_handler(
    request: Request, exc: EntityNotFoundException
):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidOperationException)
async def invalid_operation_exception_handler(
    request: Request, exc: InvalidOperationException
):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montaje de routers organizados por responsabilidad
app.include_router(teachers.router)
app.include_router(schedules.router)
app.include_router(groups.router)
app.include_router(guards.router)
app.include_router(substitutions.router)
app.include_router(absences.router)


def _frontend_dir() -> Path:
    """Build de Angular: empaquetado en el .exe o generado en Frontend/dist."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "frontend"
    return Path(__file__).resolve().parents[2] / "Frontend" / "dist" / "frontend" / "browser"


FRONTEND_DIR = _frontend_dir().resolve()

# Sirve la SPA solo si existe el build; en desarrollo se sigue usando `ng serve`.
# Debe registrarse después de los routers para no ocultar las rutas de la API.
if (FRONTEND_DIR / "index.html").is_file():

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        file = (FRONTEND_DIR / full_path).resolve()
        if file.is_file() and file.is_relative_to(FRONTEND_DIR):
            return FileResponse(file)
        return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)