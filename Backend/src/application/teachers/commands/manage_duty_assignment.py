from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.duty_type import DutyType
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class DutyAssignmentResultOut:
    message: str
    teacher_id: str
    day_of_week: int
    period: int
    duty_type: DutyType


@dataclass(frozen=True)
class AssignTeacherDutyCommand(Command[DutyAssignmentResultOut]):
    teacher_id: str
    day_of_week: int
    period: int
    duty_type: DutyType


class AssignTeacherDutyHandler(RequestHandler[AssignTeacherDutyCommand, DutyAssignmentResultOut]):
    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository

    @staticmethod
    def _validate_slot(day_of_week: int, period: int) -> None:
        if not 0 <= day_of_week <= 4:
            raise InvalidOperationException("El día debe estar entre 0 y 4.")
        if not 0 <= period <= 5:
            raise InvalidOperationException("El periodo debe estar entre 0 y 5.")

    def handle(self, cmd: AssignTeacherDutyCommand) -> DutyAssignmentResultOut:
        if not self.teacher_repository.get_by_id(cmd.teacher_id):
            raise ValueError("Profesor no encontrado.")
        self._validate_slot(cmd.day_of_week, cmd.period)
        if cmd.duty_type is DutyType.FIXED_DUTY:
            self.teacher_repository.add_fixed_duty(cmd.teacher_id, cmd.day_of_week, cmd.period)
        else:
            self.teacher_repository.add_short_term_duty(cmd.teacher_id, cmd.day_of_week, cmd.period)
        return DutyAssignmentResultOut(
            message="Asignación de guardia actualizada correctamente.",
            teacher_id=cmd.teacher_id,
            day_of_week=cmd.day_of_week,
            period=cmd.period,
            duty_type=cmd.duty_type,
        )
