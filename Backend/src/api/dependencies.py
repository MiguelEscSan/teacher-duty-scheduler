from fastapi import Depends
from sqlmodel import Session

from src.application.absences.commands.create_absence import (
    CreateAbsenceCommand,
    CreateAbsenceHandler,
)
from src.application.absences.commands.delete_absence import (
    DeleteAbsenceCommand,
    DeleteAbsenceHandler,
)
from src.application.absences.queries.get_actionable_absences import (
    GetActionableAbsencesHandler,
    GetActionableAbsencesQuery,
)
from src.application.common.mediator import Mediator
from src.application.schedules.commands.assign_slot_group import (
    AssignSlotGroupCommand,
    AssignSlotGroupHandler,
)
from src.application.schedules.queries.get_student_groups import (
    GetStudentGroupsHandler,
    GetStudentGroupsQuery,
)
from src.application.schedules.queries.get_teacher_base_schedule import (
    GetTeacherBaseScheduleHandler,
    GetTeacherBaseScheduleQuery,
)
from src.application.substitutions.commands.assign_manual_substitution import (
    AssignManualSubstitutionCommand,
    AssignManualSubstitutionHandler,
)
from src.application.substitutions.commands.mark_absence_do_not_cover import (
    MarkAbsenceDoNotCoverCommand,
    MarkAbsenceDoNotCoverHandler,
)
from src.application.substitutions.commands.notify_substitution_assignment import (
    NotifySubstitutionAssignmentCommand,
    NotifySubstitutionAssignmentHandler,
)
from src.application.substitutions.commands.resolve_substitution import (
    ResolveSubstitutionCommand,
    ResolveSubstitutionHandler,
)
from src.application.substitutions.queries.get_available_candidates import (
    GetAvailableCandidatesHandler,
    GetAvailableCandidatesQuery,
)
from src.application.substitutions.queries.get_substitution_history import (
    GetSubstitutionHistoryHandler,
    GetSubstitutionHistoryQuery,
)
from src.application.teachers.commands.create_teacher import (
    CreateTeacherCommand,
    CreateTeacherHandler,
)
from src.application.teachers.commands.delete_teacher import (
    DeleteTeacherCommand,
    DeleteTeacherHandler,
)
from src.application.teachers.queries.get_duty_teachers import (
    GetDutyTeachersHandler,
    GetDutyTeachersQuery,
)
from src.application.teachers.queries.get_short_term_teachers import (
    GetShortTermTeachersHandler,
    GetShortTermTeachersQuery,
)
from src.application.teachers.queries.get_teachers import (
    GetTeachersHandler,
    GetTeachersQuery,
)
from src.infrastructure.db.config import get_session
from src.infrastructure.email.smtp_email_sender import SMTPEmailSender
from src.infrastructure.repositories import (
    SQLAbsenceRepository,
    SQLScheduleRepository,
    SQLStudentGroupRepository,
    SQLSubstitutionRepository,
    SQLTeacherRepository,
)
from src.services.guard_service import GuardService


def get_teacher_repository(session: Session = Depends(get_session)):
    return SQLTeacherRepository(session)


def get_absence_repository(session: Session = Depends(get_session)):
    return SQLAbsenceRepository(session)


def get_schedule_repository(session: Session = Depends(get_session)):
    return SQLScheduleRepository(session)


def get_student_group_repository(session: Session = Depends(get_session)):
    return SQLStudentGroupRepository(session)


def get_substitution_repository(session: Session = Depends(get_session)):
    return SQLSubstitutionRepository(session)


def get_repository(session: Session = Depends(get_session)):
    """Compatibility dependency for callers using the old guard facade."""
    from src.infrastructure.repositories import SQLGuardRepository

    return SQLGuardRepository(session)


def get_guard_service(repo=Depends(get_repository)) -> GuardService:
    return GuardService(repository=repo)


def get_mediator(session: Session = Depends(get_session)) -> Mediator:
    teacher_repository = SQLTeacherRepository(session)
    absence_repository = SQLAbsenceRepository(session)
    schedule_repository = SQLScheduleRepository(session)
    student_group_repository = SQLStudentGroupRepository(session)
    substitution_repository = SQLSubstitutionRepository(session)
    email_sender = SMTPEmailSender()
    mediator = Mediator()

    mediator.register(
        AssignManualSubstitutionCommand,
        lambda: AssignManualSubstitutionHandler(absence_repository, substitution_repository),
    )
    mediator.register(
        ResolveSubstitutionCommand,
        lambda: ResolveSubstitutionHandler(
            teacher_repository, absence_repository, schedule_repository,
            substitution_repository, student_group_repository,
        ),
    )
    mediator.register(
        MarkAbsenceDoNotCoverCommand,
        lambda: MarkAbsenceDoNotCoverHandler(absence_repository),
    )
    mediator.register(
        NotifySubstitutionAssignmentCommand,
        lambda: NotifySubstitutionAssignmentHandler(
            teacher_repository, student_group_repository, email_sender
        ),
    )
    mediator.register(GetTeachersQuery, lambda: GetTeachersHandler(teacher_repository))
    mediator.register(
        CreateTeacherCommand, lambda: CreateTeacherHandler(teacher_repository)
    )
    mediator.register(
        DeleteTeacherCommand,
        lambda: DeleteTeacherHandler(teacher_repository, absence_repository, schedule_repository),
    )
    mediator.register(
        AssignSlotGroupCommand, lambda: AssignSlotGroupHandler(schedule_repository)
    )
    mediator.register(
        CreateAbsenceCommand,
        lambda: CreateAbsenceHandler(absence_repository, teacher_repository),
    )
    mediator.register(
        DeleteAbsenceCommand, lambda: DeleteAbsenceHandler(absence_repository)
    )
    mediator.register(
        GetAvailableCandidatesQuery,
        lambda: GetAvailableCandidatesHandler(
            teacher_repository, absence_repository, schedule_repository,
            substitution_repository,
        ),
    )
    mediator.register(
        GetSubstitutionHistoryQuery,
        lambda: GetSubstitutionHistoryHandler(
            substitution_repository, teacher_repository, student_group_repository
        ),
    )
    mediator.register(
        GetDutyTeachersQuery,
        lambda: GetDutyTeachersHandler(schedule_repository, teacher_repository),
    )
    mediator.register(
        GetShortTermTeachersQuery,
        lambda: GetShortTermTeachersHandler(schedule_repository, teacher_repository),
    )
    mediator.register(
        GetTeacherBaseScheduleQuery,
        lambda: GetTeacherBaseScheduleHandler(
            schedule_repository, student_group_repository, teacher_repository
        ),
    )
    mediator.register(
        GetStudentGroupsQuery,
        lambda: GetStudentGroupsHandler(student_group_repository),
    )
    mediator.register(
        GetActionableAbsencesQuery,
        lambda: GetActionableAbsencesHandler(
            absence_repository, teacher_repository, student_group_repository, schedule_repository
        ),
    )
    return mediator
