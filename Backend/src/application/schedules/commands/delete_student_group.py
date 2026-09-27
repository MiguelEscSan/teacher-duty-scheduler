from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.exceptions.assignment_exceptions import EntityNotFoundException
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.ports.substitution_repository import SubstitutionRepository


@dataclass(frozen=True)
class DeleteStudentGroupCommand(Command[bool]):
    group_id: str


class DeleteStudentGroupHandler(
    RequestHandler[DeleteStudentGroupCommand, bool]
):
    def __init__(
        self,
        student_group_repository: StudentGroupRepository,
        schedule_repository: ScheduleRepository,
        substitution_repository: SubstitutionRepository,
    ):
        self.student_group_repository = student_group_repository
        self.schedule_repository = schedule_repository
        self.substitution_repository = substitution_repository

    def handle(self, cmd: DeleteStudentGroupCommand) -> bool:
        if self.student_group_repository.get_by_id(cmd.group_id) is None:
            raise EntityNotFoundException(
                f"Grupo con id '{cmd.group_id}' no encontrado."
            )
        self.schedule_repository.release_slots_for_group(cmd.group_id)
        self.substitution_repository.unlink_group_from_history(cmd.group_id)
        return self.student_group_repository.delete(cmd.group_id)
