"""
Proveedores de dependencias para los controladores HTTP.
"""
from fastapi import Depends
from sqlmodel import Session

from src.infrastructure.db.config import get_session
from src.infrastructure.repositories import SQLGuardRepository
from src.services.guard_service import GuardService


def get_repository(session: Session = Depends(get_session)) -> SQLGuardRepository:
    return SQLGuardRepository(session)


def get_guard_service(
    repo: SQLGuardRepository = Depends(get_repository),
) -> GuardService:
    return GuardService(repository=repo)