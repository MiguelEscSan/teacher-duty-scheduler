from sqlmodel import Session, select
from src.infrastructure.db.models import TeacherDB, BaseScheduleDB, AbsenceDB


class SQLGuardRepository:
    def __init__(self, session: Session):
        self.session = session

    # --- Profesores ---
    def get_all_teachers(self) -> list[TeacherDB]:
        return list(self.session.exec(select(TeacherDB)).all())

    def get_teacher_by_id(self, teacher_id: str) -> TeacherDB | None:
        return self.session.get(TeacherDB, teacher_id)

    def save_teacher(self, teacher: TeacherDB) -> TeacherDB:
        self.session.add(teacher)
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def delete_teacher(self, teacher_id: str) -> bool:
        t = self.get_teacher_by_id(teacher_id)
        if not t:
            return False
        # Cascada manual
        for s in self.session.exec(select(BaseScheduleDB).where(BaseScheduleDB.teacher_id == teacher_id)):
            self.session.delete(s)
        for a in self.session.exec(select(AbsenceDB).where(AbsenceDB.teacher_id == teacher_id)):
            self.session.delete(a)
        self.session.delete(t)
        self.session.commit()
        return True

    # --- Horario Base ---
    def get_base_schedule_for_teacher(self, teacher_id: str) -> list[BaseScheduleDB]:
        return list(self.session.exec(
            select(BaseScheduleDB).where(BaseScheduleDB.teacher_id == teacher_id)
        ).all())

    def get_all_base_schedules(self) -> list[BaseScheduleDB]:
        return list(self.session.exec(select(BaseScheduleDB)).all())

    def toggle_base_slot(self, teacher_id: str, day: int, period: int) -> str:
        entry = self.session.exec(
            select(BaseScheduleDB).where(
                BaseScheduleDB.teacher_id == teacher_id,
                BaseScheduleDB.day == day,
                BaseScheduleDB.period == period
            )
        ).first()

        if entry:
            new_status = "FREE" if entry.status == "TEACHING" else "TEACHING"
            entry.status = new_status
            self.session.add(entry)
        else:
            new_status = "TEACHING"
            entry = BaseScheduleDB(teacher_id=teacher_id, day=day, period=period, status=new_status)
            self.session.add(entry)

        self.session.commit()
        return new_status

    # --- Ausencias con Fechas ---
    def get_all_absences(self) -> list[AbsenceDB]:
        return list(self.session.exec(select(AbsenceDB)).all())

    def get_absences_by_dates(self, dates: list[str]) -> list[AbsenceDB]:
        """Obtiene ausencias que coincidan con un conjunto de fechas ISO."""
        return list(self.session.exec(
            select(AbsenceDB).where(AbsenceDB.date.in_(dates))
        ).all())

    def create_absence(self, absence: AbsenceDB) -> AbsenceDB:
        self.session.add(absence)
        self.session.commit()
        self.session.refresh(absence)
        return absence

    def delete_absence(self, absence_id: int) -> bool:
        item = self.session.get(AbsenceDB, absence_id)
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True