"""
Configuración del motor de base de datos SQLite.
"""
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine, select
from src.infrastructure.db.models import TeacherDB

SQLITE_FILE_NAME = "guardias.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)

def init_db() -> None:
    """Crea las tablas y precarga datos iniciales si la base de datos está vacía."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.exec(select(TeacherDB)).first()
        if not existing:
            initial_teachers = [
                TeacherDB(id="T01", name="García Pérez, Ana"),
                TeacherDB(id="T02", name="López Martín, Carlos"),
                TeacherDB(id="T03", name="Rodríguez, Eva"),
                TeacherDB(id="T04", name="Sánchez, David"),
                TeacherDB(id="T05", name="Fernández, Lucía"),
                TeacherDB(id="T06", name="Ruiz, Mario"),
                TeacherDB(id="T07", name="Navarro, Elena"),
                TeacherDB(id="T08", name="Romero, Alberto"),
            ]
            session.add_all(initial_teachers)
            session.commit()


def get_session() -> Generator[Session, None, None]:
    """Generador de sesiones para la inyección de dependencias."""
    with Session(engine) as session:
        yield session