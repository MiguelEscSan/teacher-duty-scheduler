class DomainException(Exception):
    """Excepción base para violaciones de reglas de negocio."""
    pass

class CapacityExceededException(DomainException):
    """Lanzada cuando una fusión de grupos supera el límite físico o normativo."""
    pass