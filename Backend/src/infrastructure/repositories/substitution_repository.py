from sqlmodel import Session, func, select

from src.domain.repositories import SubstitutionRepository
from src.domain.substitution import SubstitutionLog, SubstitutionSourceType
from src.infrastructure.db.models import SubstitutionLogDB


class SQLSubstitutionRepository(SubstitutionRepository):
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_domain(item):
        source = item.source_type
        if not isinstance(source, SubstitutionSourceType):
            source = SubstitutionSourceType(source)
        return SubstitutionLog(
            id=str(item.id),
            date=item.date,
            period=item.period,
            absent_teacher_id=item.absent_teacher_id,
            substitute_teacher_id=item.substitute_teacher_id,
            source_type=source,
            group_id=item.group_id,
            created_at=item.created_at,
        )

    def get_all(self, date=None, substitute_teacher_id=None, absent_teacher_id=None):
        query = select(SubstitutionLogDB)
        if date is not None:
            query = query.where(SubstitutionLogDB.date == date)
        if substitute_teacher_id is not None:
            query = query.where(SubstitutionLogDB.substitute_teacher_id == substitute_teacher_id)
        if absent_teacher_id is not None:
            query = query.where(SubstitutionLogDB.absent_teacher_id == absent_teacher_id)
        query = query.order_by(
            SubstitutionLogDB.date.desc(),
            SubstitutionLogDB.period,
            SubstitutionLogDB.created_at.desc(),
        )
        return [self._to_domain(item) for item in self.session.exec(query).all()]

    def save(self, log):
        item = self.session.get(SubstitutionLogDB, log.id)
        if item is None:
            item = SubstitutionLogDB(id=log.id)
        item.date = log.date
        item.period = log.period
        item.absent_teacher_id = log.absent_teacher_id
        item.substitute_teacher_id = log.substitute_teacher_id
        item.group_id = log.group_id
        item.source_type = log.source_type
        item.created_at = log.created_at
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return self._to_domain(item)

    def get_busy_teacher_ids(self, date, period):
        return set(
            self.session.exec(
                select(SubstitutionLogDB.substitute_teacher_id).where(
                    SubstitutionLogDB.date == date,
                    SubstitutionLogDB.period == period,
                )
            ).all()
        )

    def get_intervention_counts(self):
        rows = self.session.exec(
            select(
                SubstitutionLogDB.substitute_teacher_id,
                func.count(SubstitutionLogDB.id),
            ).group_by(SubstitutionLogDB.substitute_teacher_id)
        ).all()
        return dict(rows)

    def get_last_used_at(self, teacher_ids, period):
        if not teacher_ids:
            return {}
        logs = self.session.exec(
            select(SubstitutionLogDB).where(
                SubstitutionLogDB.substitute_teacher_id.in_(teacher_ids),
                SubstitutionLogDB.period == period,
            ).order_by(SubstitutionLogDB.created_at.desc())
        ).all()
        result = {}
        for item in logs:
            result.setdefault(item.substitute_teacher_id, item.created_at)
        return result
