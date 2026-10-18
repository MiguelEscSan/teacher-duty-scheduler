from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_mediator
from src.api.schemas import EmailSettingsResponse, EmailSettingsUpdate, EmailTestRequest
from src.application.common.mediator import Mediator
from src.application.email.command.send_email import SendEmailCommand
from src.application.email.settings.get_email_settings import GetEmailSettingsQuery
from src.application.email.settings.save_email_settings import SaveEmailSettingsCommand

router = APIRouter(prefix="/api/v1/email", tags=["Email"])

TEST_EMAIL_SUBJECT = "Prueba de configuración del correo"
TEST_EMAIL_BODY = "Este es un correo de prueba enviado desde el Gestor de Guardias."


@router.get("/settings", response_model=EmailSettingsResponse)
def get_email_settings(mediator: Mediator = Depends(get_mediator)):
    return EmailSettingsResponse.model_validate(mediator.send(GetEmailSettingsQuery()))


@router.put("/settings", response_model=EmailSettingsResponse)
def save_email_settings(
    payload: EmailSettingsUpdate, mediator: Mediator = Depends(get_mediator)
):
    try:
        result = mediator.send(
            SaveEmailSettingsCommand(
                smtp_host=payload.smtp_host.strip(),
                smtp_port=payload.smtp_port,
                smtp_user=payload.smtp_user.strip(),
                sender_email=payload.sender_email.strip(),
                smtp_password=payload.smtp_password,
                subject_template=payload.subject_template,
                body_template=payload.body_template,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return EmailSettingsResponse.model_validate(result)


@router.post("/settings/test")
def send_test_email(payload: EmailTestRequest, mediator: Mediator = Depends(get_mediator)):
    try:
        sent = mediator.send(
            SendEmailCommand(to=payload.to, subject=TEST_EMAIL_SUBJECT, body=TEST_EMAIL_BODY)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"sent": sent}
