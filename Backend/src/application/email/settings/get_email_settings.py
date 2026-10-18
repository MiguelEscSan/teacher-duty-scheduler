# src/application/email/settings/get_email_settings.py
from dataclasses import dataclass
from typing import Callable

from src.application.common.mediator import Query, RequestHandler
from src.application.email.settings.dtos import EmailSettingsView, empty_view, view_from
from src.domain.email_settings import EmailConfiguration
from src.domain.ports.email_settings_repository import EmailSettingsRepository


@dataclass(frozen=True)
class GetEmailSettingsQuery(Query[EmailSettingsView]):
    pass


class GetEmailSettingsHandler(RequestHandler[GetEmailSettingsQuery, EmailSettingsView]):
    def __init__(
        self,
        repository: EmailSettingsRepository,
        environment_provider: Callable[[], EmailConfiguration],
    ):
        self.repository = repository
        self.environment_provider = environment_provider

    def handle(self, query: GetEmailSettingsQuery) -> EmailSettingsView:
        stored = self.repository.get()
        if stored is not None:
            return view_from(stored, "database")
        try:
            environment = self.environment_provider()
        except (RuntimeError, ValueError):
            return empty_view()
        return view_from(environment, "environment")
