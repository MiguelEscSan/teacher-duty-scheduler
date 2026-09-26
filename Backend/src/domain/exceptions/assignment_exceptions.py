from src.domain.exceptions.domain_exception import DomainException


class ConflictException(DomainException):
    """Lanzada cuando una asignación entra en conflicto con otra existente."""


class EntityNotFoundException(DomainException):
    """Lanzada cuando una entidad o asignación solicitada no existe."""
