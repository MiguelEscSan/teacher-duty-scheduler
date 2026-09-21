from sqlmodel import Session, select

from src.domain.repositories.schedule_repository import ScheduleRepository
from src.domain.schedule import ScheduleEntry
from src.infrastructure.db.models import (
    FixedDutyDB,
    ShortTermSubstitutionDB,
    TeacherScheduleDB,
)


class SQLScheduleRepository(ScheduleRepository):
    entry_type = ScheduleEntry

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_domain(item: TeacherScheduleDB) -> ScheduleEntry:
        return ScheduleEntry(
            id=item.id,
            teacher_id=item.teacher_id,
            day_of_week=item.day_of_week,
            period=item.period,
            group_id=item.group_id,
            is_teaching=item.is_teaching,
        )

    def get_for_teacher(self, teacher_id):
        return [
            self._to_domain(item)
            for item in self.session.exec(
                select(TeacherScheduleDB).where(TeacherScheduleDB.teacher_id == teacher_id)
            ).all()
        ]

    def get_all(self):
        return [self._to_domain(item) for item in self.session.exec(select(TeacherScheduleDB)).all()]

    def get_slot(self, teacher_id, day_of_week, period):
        item = self.session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.teacher_id == teacher_id,
                TeacherScheduleDB.day_of_week == day_of_week,
                TeacherScheduleDB.period == period,
            )
        ).first()
        return self._to_domain(item) if item else None

    def save(self, entry):
        item = self.session.get(TeacherScheduleDB, entry.id) if entry.id is not None else None
        if item is None:
            item = self.session.exec(
                select(TeacherScheduleDB).where(
                    TeacherScheduleDB.teacher_id == entry.teacher_id,
                    TeacherScheduleDB.day_of_week == entry.day_of_week,
                    TeacherScheduleDB.period == entry.period,
                )
            ).first()
        if item is None:
            item = TeacherScheduleDB(
                teacher_id=entry.teacher_id,
                day_of_week=entry.day_of_week,
                period=entry.period,
            )
        item.group_id = entry.group_id
        item.is_teaching = entry.is_teaching
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return self._to_domain(item)

    def delete_for_teacher(self, teacher_id):
        for item in self.session.exec(
            select(TeacherScheduleDB).where(TeacherScheduleDB.teacher_id == teacher_id)
        ).all():
            self.session.delete(item)
        self.session.commit()

    def get_fixed_duty_teacher_ids(self, day_of_week, period):
        return [
            item.teacher_id
            for item in self.session.exec(
                select(FixedDutyDB).where(
                    FixedDutyDB.day_of_week == day_of_week,
                    FixedDutyDB.period == period,
                )
            ).all()
        ]

    def get_short_term_teacher_ids(self, day_of_week, period):
        return [
            item.teacher_id
            for item in self.session.exec(
                select(ShortTermSubstitutionDB).where(
                    ShortTermSubstitutionDB.day_of_week == day_of_week,
                    ShortTermSubstitutionDB.period == period,
                )
            ).all()
        ]

    def delete_duties_for_teacher(self, teacher_id):
        for model in (FixedDutyDB, ShortTermSubstitutionDB):
            for item in self.session.exec(
                select(model).where(model.teacher_id == teacher_id)
            ).all():
                self.session.delete(item)
        self.session.commit()
