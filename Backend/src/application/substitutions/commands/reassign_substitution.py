from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.exceptions.assignment_exceptions import EntityNotFoundException
from src.domain.ports import SubstitutionRepository, TeacherRepository


@dataclass(frozen=True)
class SubstitutionResponseDto:
    id: str
    date: str
    period: int
    absent_teacher_id: str
    substitute_teacher_id: str
    source_type: str
    absent_teacher_name: str
    substitute_teacher_name: str


@dataclass(frozen=True)
class ReassignSubstitutionCommand(Command[SubstitutionResponseDto]):
    substitution_id: str
    new_substitute_teacher_id: str


# Kept as an explicit alias for callers using the terminology from the use case.
ChangeSubstitutionSubstituteCommand = ReassignSubstitutionCommand


class ReassignSubstitutionHandler(
    RequestHandler[ReassignSubstitutionCommand, SubstitutionResponseDto]
):
    def __init__(
        self,
        substitution_repository: SubstitutionRepository,
        teacher_repository: TeacherRepository,
    ):
        self.substitution_repository = substitution_repository
        self.teacher_repository = teacher_repository

    def handle(self, cmd: ReassignSubstitutionCommand) -> SubstitutionResponseDto:
        substitute = self.teacher_repository.get_by_id(cmd.new_substitute_teacher_id)
        if substitute is None:
            raise EntityNotFoundException("Docente sustituto no encontrado.")

        log = self.substitution_repository.get_by_id(cmd.substitution_id)
        if log is None:
            raise EntityNotFoundException("Registro de sustitución no encontrado.")

        log.reassign_substitute(cmd.new_substitute_teacher_id)
        self.substitution_repository.save(log)

        absent = self.teacher_repository.get_by_id(log.absent_teacher_id)
        return SubstitutionResponseDto(
            id=log.id,
            date=log.date,
            period=log.period,
            absent_teacher_id=log.absent_teacher_id,
            substitute_teacher_id=log.substitute_teacher_id,
            source_type=log.source_type.value,
            absent_teacher_name=absent.name if absent else "Profesor no encontrado",
            substitute_teacher_name=substitute.name,
        )
