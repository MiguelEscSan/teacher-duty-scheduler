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
from src.application.substitutions.services.auto_cover_teacher_duties import (
    AutoCoverTeacherDutiesService,
)
from src.application.absences.queries.get_actionable_absences import (
    GetActionableAbsencesHandler,
    GetActionableAbsencesQuery,
)
from src.application.guards.queries.calculate_week_guards import (
    CalculateWeekGuardsHandler,
    CalculateWeekGuardsQuery,
)
from src.application.common.mediator import Mediator
from src.application.schedules.commands.assign_slot_group import (
    AssignSlotGroupCommand,
    AssignSlotGroupHandler,
)
from src.application.schedules.commands.create_student_group import (
    CreateStudentGroupCommand,
    CreateStudentGroupHandler,
)
from src.application.schedules.commands.delete_student_group import (
    DeleteStudentGroupCommand,
    DeleteStudentGroupHandler,
)
from src.application.schedules.commands.update_student_group import (
    UpdateStudentGroupCommand,
    UpdateStudentGroupHandler,
)
from src.application.teachers.commands.manage_duty_assignment import (
    AssignTeacherDutyCommand,
    AssignTeacherDutyHandler,
)
from src.application.teachers.commands.remove_duty_assignment import (
    RemoveTeacherDutyCommand,
    RemoveTeacherDutyHandler,
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
from src.application.substitutions.commands.reassign_substitution import (
    ReassignSubstitutionCommand,
    ReassignSubstitutionHandler,
)
from src.application.substitutions.queries.get_available_candidates import (
    GetAvailableCandidatesHandler,
    GetAvailableCandidatesQuery,
)
from src.application.substitutions.queries.get_substitution_history import (
    GetSubstitutionHistoryHandler,
    GetSubstitutionHistoryQuery,
)
from src.application.substitutions.queries.get_interventions_summary import (
    GetSubstitutionInterventionsSummaryHandler,
    GetSubstitutionInterventionsSummaryQuery,
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
from src.infrastructure.optimization.ortools_guard_optimizer import ORToolsGuardOptimizer
from src.infrastructure.repositories import (
    SQLAbsenceRepository,
    SQLScheduleRepository,
    SQLStudentGroupRepository,
    SQLSubstitutionRepository,
    SQLTeacherRepository,
)


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


def get_mediator(session: Session = Depends(get_session)) -> Mediator:
    teacher_repository = SQLTeacherRepository(session)
    absence_repository = SQLAbsenceRepository(session)
    schedule_repository = SQLScheduleRepository(session)
    student_group_repository = SQLStudentGroupRepository(session)
    substitution_repository = SQLSubstitutionRepository(session)
    email_sender = SMTPEmailSender()
    auto_cover_service = AutoCoverTeacherDutiesService(
        teacher_repository,
        absence_repository,
        schedule_repository,
        substitution_repository,
    )
    optimizer = ORToolsGuardOptimizer()
    mediator = Mediator()

    mediator.register(
        CalculateWeekGuardsQuery,
        lambda: CalculateWeekGuardsHandler(
            teacher_repository, schedule_repository, absence_repository, optimizer
        ),
    )
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
        ReassignSubstitutionCommand,
        lambda: ReassignSubstitutionHandler(
            substitution_repository, teacher_repository
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
        CreateStudentGroupCommand,
        lambda: CreateStudentGroupHandler(student_group_repository),
    )
    mediator.register(
        UpdateStudentGroupCommand,
        lambda: UpdateStudentGroupHandler(student_group_repository),
    )
    mediator.register(
        DeleteStudentGroupCommand,
        lambda: DeleteStudentGroupHandler(
            student_group_repository,
            schedule_repository,
            substitution_repository,
        ),
    )
    mediator.register(
        AssignTeacherDutyCommand,
        lambda: AssignTeacherDutyHandler(teacher_repository),
    )
    mediator.register(
        RemoveTeacherDutyCommand,
        lambda: RemoveTeacherDutyHandler(teacher_repository),
    )
    mediator.register(
        CreateAbsenceCommand,
        lambda: CreateAbsenceHandler(
            absence_repository,
            teacher_repository,
            substitution_repository,
            auto_cover_service,
        ),
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
        GetSubstitutionInterventionsSummaryQuery,
        lambda: GetSubstitutionInterventionsSummaryHandler(
            substitution_repository, teacher_repository
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
