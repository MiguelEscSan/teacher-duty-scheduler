from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.ports.absence_repository import AbsenceRepository


@dataclass(frozen=True)
class DeleteAbsenceCommand(Command[bool]):
    absence_id: str


class DeleteAbsenceHandler(RequestHandler[DeleteAbsenceCommand, bool]):
    def __init__(self, absence_repository: AbsenceRepository):
        self.absence_repository = absence_repository

    def handle(self, cmd: DeleteAbsenceCommand) -> bool:
        return self.absence_repository.delete(cmd.absence_id)
