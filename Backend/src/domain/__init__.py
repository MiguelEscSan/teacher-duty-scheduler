from src.domain.absence import Absence
from src.domain.guard import AssignmentReport, GuardAssignment
from src.domain.schedule import ScheduleEntry, ScheduleSlot, SlotStatus, TeacherSchedule, TimeSlot
from src.domain.student_group import StudentGroup
from src.domain.substitution import SubstitutionLog, SubstitutionSourceType
from src.domain.teacher import CorporateEmail, Teacher
from src.domain.exceptions.absence_already_resolved_exception import AbsenceAlreadyResolvedException
from src.domain.exceptions.domain_exception import CapacityExceededException, DomainException
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException, SlotCollisionException

__all__ = [
    "Absence", "AbsenceAlreadyResolvedException", "AssignmentReport",
    "CapacityExceededException", "CorporateEmail", "DomainException",
    "GuardAssignment", "InvalidOperationException", "ScheduleSlot",
    "SlotCollisionException", "SlotStatus", "StudentGroup", "SubstitutionLog",
    "SubstitutionSourceType", "Teacher", "TeacherSchedule", "TimeSlot", "ScheduleEntry",
]
