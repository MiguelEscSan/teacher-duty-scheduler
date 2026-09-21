from dataclasses import dataclass
from src.application.common.mediator import Command
from sqlmodel import Session
from src.api.schemas import TeacherResponse
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import TeacherDB


@dataclass(frozen=True)
class CreateTeacherCommand(Command[TeacherResponse]):
    name: str
    department: str = "General"


class CreateTeacherHandler(RequestHandler[CreateTeacherCommand, TeacherResponse]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, cmd: CreateTeacherCommand) -> TeacherResponse:
        # Generar correo corporativo estándar por convención
        alias = (
            cmd.name.split(",")[0].strip().lower().replace(" ", "")
            .replace("á", "a").replace("é", "e").replace("í", "i")
            .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
        )
        email = f"{alias}@centroeducativo.es"

        new_teacher = TeacherDB(
            name=cmd.name,
            department=cmd.department,
            email=email,
        )
        self.session.add(new_teacher)
        self.session.commit()
        self.session.refresh(new_teacher)

        return TeacherResponse(
            id=new_teacher.id,
            name=new_teacher.name,
            department=new_teacher.department,
        )