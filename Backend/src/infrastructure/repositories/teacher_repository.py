from sqlmodel import Session, select

from src.domain.teacher import CorporateEmail, Teacher
from src.domain.ports.teacher_repository import TeacherRepository
from src.infrastructure.db.models import TeacherDB


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
        self.session.commit()
        self.session.refresh(item)
        return self._to_domain(item)

    def delete(self, teacher_id: str) -> bool:
        item = self.session.get(TeacherDB, teacher_id)
        if item is None:
            return False
        self.session.delete(item)
        self.session.commit()
        return True
