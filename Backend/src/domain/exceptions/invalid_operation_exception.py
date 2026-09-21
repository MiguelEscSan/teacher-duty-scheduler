from src.domain.exceptions.domain_exception import DomainException

class InvalidOperationException(DomainException):
    """Lanzada cuando una entidad se encuentra en un estado que no permite la acción."""
    pass


class SlotCollisionException(InvalidOperationException):
    """Lanzada cuando se intenta asignar una tarea a un docente ya ocupado."""
    pass
