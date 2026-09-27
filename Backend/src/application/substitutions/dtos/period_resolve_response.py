from dataclasses import dataclass


@dataclass(frozen=True)
class PeriodResolveResponseDto:
    date: str
    period: int
    resolved: bool
    action_applied: str
    substitute_id: str | None = None
    substitute_name: str | None = None
    substitute_email: str | None = None
    source_type: str | None = None
    is_short_term_substitute: bool = False
    is_fixed_duty_substitute: bool = False
    staff_room_keeper_name: str | None = None
    email_notification_dispatched: bool = False
    details: str = ""
