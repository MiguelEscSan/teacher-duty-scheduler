"""
Configuración del motor de base de datos SQLite.
"""
import os
from pathlib import Path
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine

SQLITE_FILE_NAME = "guardias.db"
DB_DIR = Path(os.getenv("DB_DIR", "."))
os.makedirs(DB_DIR, exist_ok=True)
SQLITE_URL = f"sqlite:///{DB_DIR / SQLITE_FILE_NAME}"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)

def init_db() -> None:
    """Crea las tablas y precarga datos iniciales si la base de datos está vacía."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Generador de sesiones para la inyección de dependencias."""
    with Session(engine) as session:
        yield session