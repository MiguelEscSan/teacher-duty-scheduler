from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from src.api.dependencies import get_session, get_mediator
from src.api.schemas import (
    AvailableTeacherOut,
    ManualAssignmentIn,
    PeriodResolveRequest,
    PeriodResolveResponse,
    SubstitutionEmailRequest,
    DoNotCoverRequest,
    SubstitutionHistoryOut,
)
from src.application.common.mediator import Mediator
from src.application.substitutions.commands.assign_manual_substitution import AssignManualSubstitutionCommand
from src.application.substitutions.commands.mark_absence_do_not_cover import MarkAbsenceDoNotCoverCommand
from src.application.substitutions.commands.resolve_substitution import ResolveSubstitutionCommand
from src.application.substitutions.queries.get_available_candidates import GetAvailableCandidatesQuery
from src.application.substitutions.queries.get_substitution_history import GetSubstitutionHistoryQuery
from src.infrastructure.db.models import AbsenceDB

router = APIRouter(prefix="/api/v1/substitutions", tags=["Sustituciones Operativas"])

@router.get("/history", response_model=List[SubstitutionHistoryOut])
def get_substitution_history(
    date: str | None = Query(default=None),
    substitute_teacher_id: str | None = Query(default=None),
    absent_teacher_id: str | None = Query(default=None),
    mediator: Mediator = Depends(get_mediator),
):
    return mediator.send(
        GetSubstitutionHistoryQuery(
            date=date,
            substitute_teacher_id=substitute_teacher_id,
            absent_teacher_id=absent_teacher_id,
        )
    )

@router.post("/resolve", response_model=PeriodResolveResponse)
def resolve_substitution(
    payload: PeriodResolveRequest,
    mediator: Mediator = Depends(get_mediator),
):
    try:
        return mediator.send(
            ResolveSubstitutionCommand(
                date=payload.date,
                period=payload.period,
                absent_teacher_id=payload.absent_teacher_id,
                action=payload.action,
                group_id=payload.group_id,
                merged_with_group_id=payload.merged_with_group_id,
            )
        )
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))

@router.post("/send-email")
def send_substitution_email(
    payload: SubstitutionEmailRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    return {"message": "Correo de sustitución programado correctamente."}


@router.post("/do-not-cover")
def mark_absence_as_do_not_cover(
    payload: DoNotCoverRequest,
    mediator: Mediator = Depends(get_mediator),
):
    try:
        return mediator.send(
            MarkAbsenceDoNotCoverCommand(
                date=payload.date,
                period=payload.period,
                absent_teacher_id=payload.absent_teacher_id,
            )
        )
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.get("/available-candidates", response_model=List[AvailableTeacherOut])
def get_available_candidates(
    date_str: str,
    period: int,
    mediator: Mediator = Depends(get_mediator)
):
    query = GetAvailableCandidatesQuery(date_str=date_str, period=period)
    return mediator.send(query)

@router.post("/assign-manual", status_code=status.HTTP_201_CREATED)
def assign_manual_substitution(
    payload: ManualAssignmentIn,
    mediator: Mediator = Depends(get_mediator)
):
    cmd = AssignManualSubstitutionCommand(
        date=payload.date,
        period=payload.period,
        absent_teacher_id=payload.absent_teacher_id,
        substitute_teacher_id=payload.substitute_teacher_id,
        group_id=payload.group_id,
        notes=payload.notes,
    )
    return mediator.send(cmd)

