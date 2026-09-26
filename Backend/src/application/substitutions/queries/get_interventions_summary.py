from dataclasses import dataclass

from src.api.schemas import SubstitutionInterventionsSummaryOut
from src.application.common.mediator import Query, RequestHandler
from src.domain.ports.substitution_repository import SubstitutionRepository
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetSubstitutionInterventionsSummaryQuery(
    Query[list[SubstitutionInterventionsSummaryOut]]
):
    pass


class GetSubstitutionInterventionsSummaryHandler(
    RequestHandler[
        GetSubstitutionInterventionsSummaryQuery,
        list[SubstitutionInterventionsSummaryOut],
    ]
):
    def __init__(
        self,
        substitution_repository: SubstitutionRepository,
        teacher_repository: TeacherRepository,
    ):
        self.substitution_repository = substitution_repository
        self.teacher_repository = teacher_repository

    def handle(
        self, query: GetSubstitutionInterventionsSummaryQuery
    ) -> list[SubstitutionInterventionsSummaryOut]:
        breakdown = self.substitution_repository.get_interventions_breakdown_by_teacher()
        return [
            SubstitutionInterventionsSummaryOut(
                teacher_id=teacher.id,
                teacher_name=teacher.name,
                ordinary_guard_count=breakdown.get(teacher.id, {}).get(
                    "ORDINARY_GUARD", 0
                ),
                short_term_count=breakdown.get(teacher.id, {}).get(
                    "SHORT_TERM_SUBSTITUTION", 0
                ),
                manual_count=breakdown.get(teacher.id, {}).get("MANUAL", 0),
                total_interventions=breakdown.get(teacher.id, {}).get("TOTAL", 0),
            )
            for teacher in self.teacher_repository.get_all()
        ]
