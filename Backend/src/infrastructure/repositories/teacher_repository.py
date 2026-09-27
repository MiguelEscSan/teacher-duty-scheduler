from sqlmodel import Session, select

from src.domain.teacher import CorporateEmail, Teacher
from src.domain.ports.teacher_repository import TeacherRepository
from src.infrastructure.db.models import (
    FixedDutyDB,
    ShortTermSubstitutionDB,
    TeacherDB,
    TeacherScheduleDB,
)


class SQLTeacherRepository(TeacherRepository):
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_domain(model: TeacherDB) -> Teacher:
        return Teacher(
            id=model.id,
            name=model.name,
            department=model.department,
            email=CorporateEmail(model.email) if model.email else None,
        )

    def get_all(self) -> list[Teacher]:
        return [self._to_domain(item) for item in self.session.exec(select(TeacherDB)).all()]

    def get_by_id(self, teacher_id: str) -> Teacher | None:
        item = self.session.get(TeacherDB, teacher_id)
        return self._to_domain(item) if item else None

    def save(self, teacher: Teacher) -> Teacher:
        item = self.session.get(TeacherDB, teacher.id)
        if item is None:
            item = TeacherDB(id=teacher.id, name=teacher.name, department=teacher.department)
        item.name = teacher.name
        item.department = teacher.department
        item.email = str(teacher.email) if teacher.email else None
        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return self._to_domain(item)

    def delete(self, teacher_id: str) -> bool:
        item = self.session.get(TeacherDB, teacher_id)
        if item is None:
            return False
        self.session.delete(item)
        return True

    def _set_fixed_duty_schedule_state(
        self, teacher_id: str, day_of_week: int, period: int, is_teaching: bool
    ) -> None:
        schedule = self.session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.teacher_id == teacher_id,
                TeacherScheduleDB.day_of_week == day_of_week,
                TeacherScheduleDB.period == period,
            )
        ).first()
        if schedule is not None:
            schedule.is_teaching = is_teaching
            schedule.slot_type = "TEACHING" if is_teaching else "FREE"
            self.session.add(schedule)

    def add_fixed_duty(self, teacher_id: str, day_of_week: int, period: int) -> None:
        existing = self.session.exec(
            select(FixedDutyDB).where(
                FixedDutyDB.teacher_id == teacher_id,
                FixedDutyDB.day_of_week == day_of_week,
                FixedDutyDB.period == period,
            )
        ).first()
        if existing is None:
            self.session.add(
                FixedDutyDB(
                    teacher_id=teacher_id,
                    day_of_week=day_of_week,
                    period=period,
                )
            )
        self._set_fixed_duty_schedule_state(teacher_id, day_of_week, period, False)

    def remove_fixed_duty(self, teacher_id: str, day_of_week: int, period: int) -> bool:
        item = self.session.exec(
            select(FixedDutyDB).where(
                FixedDutyDB.teacher_id == teacher_id,
                FixedDutyDB.day_of_week == day_of_week,
                FixedDutyDB.period == period,
            )
        ).first()
        if item is None:
            return False
        self.session.delete(item)
        schedule = self.session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.teacher_id == teacher_id,
                TeacherScheduleDB.day_of_week == day_of_week,
                TeacherScheduleDB.period == period,
            )
        ).first()
        if schedule is not None:
            schedule.is_teaching = schedule.group_id is not None
            if schedule.is_teaching:
                schedule.slot_type = "TEACHING"
            self.session.add(schedule)
        return True

    def add_short_term_duty(self, teacher_id: str, day_of_week: int, period: int) -> None:
        existing = self.session.exec(
            select(ShortTermSubstitutionDB).where(
                ShortTermSubstitutionDB.teacher_id == teacher_id,
                ShortTermSubstitutionDB.day_of_week == day_of_week,
                ShortTermSubstitutionDB.period == period,
            )
        ).first()
        if existing is None:
            self.session.add(
                ShortTermSubstitutionDB(
                    teacher_id=teacher_id,
                    day_of_week=day_of_week,
                    period=period,
                )
            )

    def remove_short_term_duty(
        self, teacher_id: str, day_of_week: int, period: int
    ) -> bool:
        item = self.session.exec(
            select(ShortTermSubstitutionDB).where(
                ShortTermSubstitutionDB.teacher_id == teacher_id,
                ShortTermSubstitutionDB.day_of_week == day_of_week,
                ShortTermSubstitutionDB.period == period,
            )
        ).first()
        if item is None:
            return False
        self.session.delete(item)
        return True

    def is_teacher_in_fixed_duty(
        self, teacher_id: str, day_of_week: int, period: int
    ) -> bool:
        return self.session.exec(
            select(FixedDutyDB).where(
                FixedDutyDB.teacher_id == teacher_id,
                FixedDutyDB.day_of_week == day_of_week,
                FixedDutyDB.period == period,
            )
        ).first() is not None

    def is_teacher_in_short_term_duty(
        self, teacher_id: str, day_of_week: int, period: int
    ) -> bool:
        return self.session.exec(
            select(ShortTermSubstitutionDB).where(
                ShortTermSubstitutionDB.teacher_id == teacher_id,
                ShortTermSubstitutionDB.day_of_week == day_of_week,
                ShortTermSubstitutionDB.period == period,
            )
        ).first() is not None
