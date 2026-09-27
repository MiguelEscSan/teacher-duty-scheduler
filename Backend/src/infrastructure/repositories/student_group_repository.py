from sqlmodel import Session, select

from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.student_group import StudentGroup
from src.infrastructure.db.models import StudentGroupDB


class SQLStudentGroupRepository(StudentGroupRepository):
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_domain(item: StudentGroupDB) -> StudentGroup:
        count = item.student_count
        capacity = max(30, count) if count is not None else 30
        return StudentGroup(
            id=item.id,
            name=item.name,
            student_count=count,
            max_capacity=capacity,
        )

    def get_all(self) -> list[StudentGroup]:
        return [self._to_domain(item) for item in self.session.exec(select(StudentGroupDB)).all()]

    def get_by_id(self, group_id: str) -> StudentGroup | None:
        item = self.session.get(StudentGroupDB, group_id)
        return self._to_domain(item) if item else None

    def get_by_name(self, name: str) -> StudentGroup | None:
        item = self.session.exec(
            select(StudentGroupDB).where(StudentGroupDB.name == name)
        ).first()
        return self._to_domain(item) if item else None

    def save(self, group: StudentGroup) -> None:
        record = self.session.get(StudentGroupDB, group.id)
        if record is None:
            record = StudentGroupDB(
                id=group.id,
                name=group.name,
                student_count=group.student_count,
            )
            self.session.add(record)
        else:
            record.name = group.name
            record.student_count = group.student_count
        self.session.commit()

    def delete(self, group_id: str) -> bool:
        record = self.session.get(StudentGroupDB, group_id)
        if record is None:
            return False
        self.session.delete(record)
        self.session.commit()
        return True
