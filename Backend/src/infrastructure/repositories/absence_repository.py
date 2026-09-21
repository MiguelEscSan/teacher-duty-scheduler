from sqlmodel import Session, select

from src.domain.absence import Absence
from src.domain.repositories.absence_repository import AbsenceRepository
from src.infrastructure.db.models import AbsenceDB


class SQLAbsenceRepository(AbsenceRepository):
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_domain(item: AbsenceDB) -> Absence:
        return Absence(
            id=item.id,
            teacher_id=item.teacher_id,
            date=item.date,
            period=item.period,
            reason=item.reason,
            resolved=item.resolved,
        )

    @staticmethod
    def _to_model(entity: Absence) -> AbsenceDB:
        return AbsenceDB(
            id=entity.id,
            teacher_id=entity.teacher_id,
            date=entity.date,
            period=entity.period,
            reason=entity.reason,
            resolved=entity.resolved,
        )

    def _query(self):
        return select(AbsenceDB)

    def get_all(self, date=None, teacher_id=None, resolved=None) -> list[Absence]:
        query = self._query()
        if date is not None:
            query = query.where(AbsenceDB.date == date)
        if teacher_id is not None:
            query = query.where(AbsenceDB.teacher_id == teacher_id)
        if resolved is not None:
            query = query.where(AbsenceDB.resolved == resolved)
        return [self._to_domain(item) for item in self.session.exec(query).all()]

    def get_by_id(self, absence_id: str) -> Absence | None:
        item = self.session.get(AbsenceDB, absence_id)
        return self._to_domain(item) if item else None

    def get_by_slot(self, teacher_id, date, period):
        item = self.session.exec(
            select(AbsenceDB).where(
                AbsenceDB.teacher_id == teacher_id,
                AbsenceDB.date == date,
                AbsenceDB.period == period,
            )
        ).first()
        return self._to_domain(item) if item else None

    def get_by_dates(self, dates):
        return [
            self._to_domain(item)
            for item in self.session.exec(select(AbsenceDB).where(AbsenceDB.date.in_(dates))).all()
        ]

    def save(self, absence):
        item = self.session.get(AbsenceDB, absence.id)
        if item is None:
            item = self._to_model(absence)
        else:
            item.teacher_id = absence.teacher_id
            item.date = absence.date
            item.period = absence.period
            item.reason = absence.reason
            item.resolved = absence.resolved
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return self._to_domain(item)

    def delete(self, absence_id):
        item = self.session.get(AbsenceDB, absence_id)
        if item is None:
            return False
        self.session.delete(item)
        self.session.commit()
        return True
