from dataclasses import dataclass
from src.application.common.mediator import Command
from sqlmodel import Session
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import AbsenceDB

@dataclass(frozen=True)
class DeleteAbsenceCommand(Command[bool]):
    absence_id: str

class DeleteAbsenceHandler(RequestHandler[DeleteAbsenceCommand, bool]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, cmd: DeleteAbsenceCommand) -> bool:
        item = self.session.get(AbsenceDB, cmd.absence_id)
        if not item:
            return False

        self.session.delete(item)
        self.session.commit()
        return True