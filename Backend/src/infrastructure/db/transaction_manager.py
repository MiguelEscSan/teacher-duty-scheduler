from sqlmodel import Session

from src.domain.ports.transaction_manager import TransactionManager


class SQLTransactionManager(TransactionManager):
    """Transaction boundary for repositories sharing one SQLModel session."""

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self) -> "SQLTransactionManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
