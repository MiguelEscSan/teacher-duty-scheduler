from sqlmodel import Session, func, select

from src.domain.ports import SubstitutionRepository
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

    def get_by_id(self, substitution_id):
        item = self.session.get(SubstitutionLogDB, substitution_id)
        return self._to_domain(item) if item else None

    def get_by_slot(self, date, period, absent_teacher_id):
        item = self.session.exec(
            select(SubstitutionLogDB).where(
                SubstitutionLogDB.date == date,
                SubstitutionLogDB.period == period,
                SubstitutionLogDB.absent_teacher_id == absent_teacher_id,
            )
        ).first()
        return self._to_domain(item) if item else None

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
            item = SubstitutionLogDB(
                id=log.id,
                date=log.date,
                period=log.period,
                absent_teacher_id=log.absent_teacher_id,
                substitute_teacher_id=log.substitute_teacher_id,
                group_id=log.group_id,
                source_type=log.source_type,
                created_at=log.created_at,
            )
        else:
            item.substitute_teacher_id = log.substitute_teacher_id
            item.source_type = log.source_type
        item.date = log.date
        item.period = log.period
        item.absent_teacher_id = log.absent_teacher_id
        item.group_id = log.group_id
        item.created_at = log.created_at
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

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

    def get_interventions_breakdown_by_teacher(self):
        rows = self.session.exec(
            select(
                SubstitutionLogDB.substitute_teacher_id,
                SubstitutionLogDB.source_type,
                func.count(SubstitutionLogDB.id),
            ).group_by(
                SubstitutionLogDB.substitute_teacher_id,
                SubstitutionLogDB.source_type,
            )
        ).all()
        result = {}
        for teacher_id, source_type, count in rows:
            source = source_type.value if isinstance(source_type, SubstitutionSourceType) else str(source_type)
            bucket = result.setdefault(
                teacher_id,
                {
                    "ORDINARY_GUARD": 0,
                    "SHORT_TERM_SUBSTITUTION": 0,
                    "MANUAL": 0,
                    "TOTAL": 0,
                },
            )
            if source not in ("ORDINARY_GUARD", "SHORT_TERM_SUBSTITUTION"):
                source = "MANUAL"
            bucket[source] += count
            bucket["TOTAL"] += count
        return result

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
