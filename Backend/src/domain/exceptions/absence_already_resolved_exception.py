from src.domain.exceptions.invalid_operation_exception import InvalidOperationException


class AbsenceAlreadyResolvedException(InvalidOperationException):
    def __init__(self, absence_id: str):
        super().__init__(f"La ausencia '{absence_id}' ya fue resuelta previamente.")