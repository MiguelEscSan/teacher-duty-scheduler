from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.exceptions.assignment_exceptions import EntityNotFoundException
from src.domain.ports.student_group_repository import StudentGroupRepository


@dataclass(frozen=True)
class DeleteStudentGroupCommand(Command[None]):
    group_id: str


class DeleteStudentGroupHandler(
    RequestHandler[DeleteStudentGroupCommand, None]
):
    def __init__(self, student_group_repository: StudentGroupRepository):
        self.student_group_repository = student_group_repository

    def handle(self, cmd: DeleteStudentGroupCommand) -> None:
        if self.student_group_repository.get_by_id(cmd.group_id) is None:
            raise EntityNotFoundException("Grupo de alumnos no encontrado.")
        self.student_group_repository.delete(cmd.group_id)
