# src/application/common/mediator.py
from typing import Any, Callable, Dict, Generic, Type, TypeVar
from dataclasses import dataclass

TResult = TypeVar("TResult")
TRequest = TypeVar("TRequest")


class Request(Generic[TResult]):
    """Mensaje base (Comando o Consulta) que espera un resultado de tipo TResult."""
    pass


class Command(Request[TResult]):
    """Marca explícita de intención de mutación de estado."""
    pass


class Query(Request[TResult]):
    """Marca explícita de intención de lectura sin efectos secundarios."""
    pass


class RequestHandler(Generic[TRequest, TResult]):
    """Interfaz base para el manejador de una petición."""

    def handle(self, request: TRequest) -> TResult:
        raise NotImplementedError


class Mediator:
    """
    Despachador en memoria para desacoplar el origen de la petición
    de su ejecutor concreto.
    """

    def __init__(self):
        self._handlers: Dict[Type[Request], Callable[[], RequestHandler]] = {}

    def register(
            self,
            request_type: Type[Request[TResult]],
            handler_factory: Callable[[], RequestHandler[Any, TResult]]
    ) -> None:
        """Registra una factoría para resolver el Handler bajo demanda."""
        self._handlers[request_type] = handler_factory

    def send(self, request: Request[TResult]) -> TResult:
        """Encuentra el handler asociado y ejecuta la solicitud."""
        request_type = type(request)
        handler_factory = self._handlers.get(request_type)

        if not handler_factory:
            raise KeyError(f"No hay handler registrado para {request_type.__name__}")

        handler = handler_factory()
        return handler.handle(request)