from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.repositories.absence_repository import AbsenceRepository
from src.domain.repositories.schedule_repository import ScheduleRepository
from src.domain.repositories.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class DeleteTeacherCommand(Command[bool]):
    teacher_id: str


class DeleteTeacherHandler(RequestHandler[DeleteTeacherCommand, bool]):
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        absence_repository: AbsenceRepository,
        schedule_repository: ScheduleRepository,
    ):
        self.teacher_repository = teacher_repository
        self.absence_repository = absence_repository
        self.schedule_repository = schedule_repository

    def handle(self, cmd: DeleteTeacherCommand) -> bool:
        if not self.teacher_repository.get_by_id(cmd.teacher_id):
            return False
        for absence in self.absence_repository.get_all(teacher_id=cmd.teacher_id):
            self.absence_repository.delete(absence.id)
        self.schedule_repository.delete_for_teacher(cmd.teacher_id)
        self.schedule_repository.delete_duties_for_teacher(cmd.teacher_id)
        return self.teacher_repository.delete(cmd.teacher_id)
