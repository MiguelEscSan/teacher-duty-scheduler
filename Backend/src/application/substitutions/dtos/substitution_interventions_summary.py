from dataclasses import dataclass


@dataclass(frozen=True)
class SubstitutionInterventionsSummaryDto:
    teacher_id: str
    teacher_name: str
    ordinary_guard_count: int
    short_term_count: int
    manual_count: int
    total_interventions: int
