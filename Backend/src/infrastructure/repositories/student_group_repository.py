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

    def get_all(self):
        return [self._to_domain(item) for item in self.session.exec(select(StudentGroupDB)).all()]

    def get_by_id(self, group_id):
        item = self.session.get(StudentGroupDB, group_id)
        return self._to_domain(item) if item else None
