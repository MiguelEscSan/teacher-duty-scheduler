"""
Configuración del motor de base de datos SQLite.
"""
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import inspect, text
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
    # create_all does not alter an existing SQLite table.
    with engine.begin() as connection:
        columns = {column["name"] for column in inspect(connection).get_columns("teacher_schedules")}
        if columns and "slot_type" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE teacher_schedules "
                    "ADD COLUMN slot_type VARCHAR NOT NULL DEFAULT 'FREE'"
                )
            )


def get_session() -> Generator[Session, None, None]:
    """Generador de sesiones para la inyección de dependencias."""
    with Session(engine) as session:
        yield session