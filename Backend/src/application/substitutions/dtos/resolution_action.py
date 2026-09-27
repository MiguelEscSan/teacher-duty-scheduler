from enum import Enum


class ResolutionAction(str, Enum):
    AUTO_ASSIGN = "AUTO_ASSIGN"
    EXCURSION = "EXCURSION"
    MERGE_GROUPS = "MERGE_GROUPS"
    FORCE_SHORT_TERM = "FORCE_SHORT_TERM"
