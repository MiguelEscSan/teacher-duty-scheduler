from enum import Enum


class DutyType(str, Enum):
    FIXED_DUTY = "FIXED_DUTY"
    SHORT_TERM = "SHORT_TERM"
