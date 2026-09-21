"""
Proveedores de dependencias para los controladores HTTP.
"""
from fastapi import Depends
from sqlmodel import Session

from src.application.substitutions.commands.mark_absence_do_not_cover import MarkAbsenceDoNotCoverCommand, \
    MarkAbsenceDoNotCoverHandler
from src.application.substitutions.commands.resolve_substitution import ResolveSubstitutionCommand, ResolveSubstitutionHandler
from src.application.substitutions.queries.get_available_candidates import GetAvailableCandidatesQuery, GetAvailableCandidatesHandler
from src.application.teachers.commands.create_teacher import CreateTeacherCommand, CreateTeacherHandler
from src.application.teachers.commands.delete_teacher import DeleteTeacherCommand, DeleteTeacherHandler
from src.application.teachers.queries.get_duty_teachers import GetDutyTeachersQuery, GetDutyTeachersHandler
from src.application.teachers.queries.get_short_term_teachers import GetShortTermTeachersQuery, GetShortTermTeachersHandler
from src.application.substitutions.queries.get_substitution_history import GetSubstitutionHistoryQuery, GetSubstitutionHistoryHandler
from src.application.teachers.queries.get_teachers import GetTeachersQuery, GetTeachersHandler
from src.infrastructure.db.config import get_session
from src.infrastructure.repositories import SQLGuardRepository
from src.services.guard_service import GuardService
from src.application.common.mediator import Mediator

# Comandos y Handlers
from src.application.substitutions.commands.assign_manual_substitution import (
    AssignManualSubstitutionCommand,
    AssignManualSubstitutionHandler,
)

def get_repository(session: Session = Depends(get_session)) -> SQLGuardRepository:
    return SQLGuardRepository(session)


def get_guard_service(
    repo: SQLGuardRepository = Depends(get_repository),
) -> GuardService:
    return GuardService(repository=repo)

def get_mediator(session: Session = Depends(get_session)) -> Mediator:
    mediator = Mediator()

    # Comandos
    mediator.register(AssignManualSubstitutionCommand, lambda: AssignManualSubstitutionHandler(session))
    mediator.register(ResolveSubstitutionCommand, lambda: ResolveSubstitutionHandler(session))
    mediator.register(MarkAbsenceDoNotCoverCommand, lambda: MarkAbsenceDoNotCoverHandler(session))
    mediator.register(GetTeachersQuery, lambda: GetTeachersHandler(session))
    mediator.register(CreateTeacherCommand, lambda: CreateTeacherHandler(session))
    mediator.register(DeleteTeacherCommand, lambda: DeleteTeacherHandler(session))

    # Queries
    mediator.register(GetAvailableCandidatesQuery, lambda: GetAvailableCandidatesHandler(session))
    mediator.register(GetSubstitutionHistoryQuery, lambda: GetSubstitutionHistoryHandler(session))
    mediator.register(GetDutyTeachersQuery, lambda: GetDutyTeachersHandler(session))
    mediator.register(GetShortTermTeachersQuery, lambda: GetShortTermTeachersHandler(session))

    return mediator