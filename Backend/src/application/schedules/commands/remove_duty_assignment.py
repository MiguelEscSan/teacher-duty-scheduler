from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.application.schedules.commands.manage_duty_assignment import (
    AssignTeacherDutyHandler,
    DutyAssignmentResultOut,
)
from src.domain.duty_type import DutyType
from src.domain.exceptions.assignment_exceptions import EntityNotFoundException
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class RemoveTeacherDutyCommand(Command[DutyAssignmentResultOut]):
    teacher_id: str
    day_of_week: int
    period: int
    duty_type: DutyType


class RemoveTeacherDutyHandler(RequestHandler[RemoveTeacherDutyCommand, DutyAssignmentResultOut]):
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        schedule_repository: ScheduleRepository,
    ):
        self.teacher_repository = teacher_repository
        self.schedule_repository = schedule_repository

    def handle(self, cmd: RemoveTeacherDutyCommand) -> DutyAssignmentResultOut:
        if not self.teacher_repository.get_by_id(cmd.teacher_id):
            raise ValueError("Profesor no encontrado.")
        AssignTeacherDutyHandler._validate_slot(cmd.day_of_week, cmd.period)
        if cmd.duty_type is DutyType.FIXED_DUTY:
            removed = self.schedule_repository.remove_fixed_duty(
                cmd.teacher_id, cmd.day_of_week, cmd.period
            )
        else:
            removed = self.schedule_repository.remove_short_term_duty(
                cmd.teacher_id, cmd.day_of_week, cmd.period
            )
        if not removed:
            raise EntityNotFoundException("El profesor no está asignado a esa franja.")
        return DutyAssignmentResultOut(
            message="Asignación de guardia eliminada correctamente.",
            teacher_id=cmd.teacher_id,
            day_of_week=cmd.day_of_week,
            period=cmd.period,
            duty_type=cmd.duty_type,
        )
