from datetime import datetime

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.api.dependencies import get_session
from src.domain.absence import Absence
from src.domain.teacher import Teacher
from src.main import app


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def client(db_session, monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setattr("src.main.init_db", lambda: None)

    def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class FakeAbsenceRepository:
    def __init__(self, absences=None):
        self.items = list(absences or [])

    def get_all(self, date=None, teacher_id=None, resolved=None):
        return [
            item for item in self.items
            if (date is None or item.date == date)
            and (teacher_id is None or item.teacher_id == teacher_id)
            and (resolved is None or item.resolved == resolved)
        ]

    def get_by_id(self, absence_id):
        return next((item for item in self.items if item.id == absence_id), None)

    def get_by_slot(self, teacher_id, date, period):
        return next(
            (item for item in self.items if item.teacher_id == teacher_id
             and item.date == date and item.period == period),
            None,
        )

    def get_by_dates(self, dates):
        return [item for item in self.items if item.date in dates]

    def save(self, absence):
        old = self.get_by_id(absence.id)
        if old is None:
            self.items.append(absence)
        else:
            self.items[self.items.index(old)] = absence
        return absence

    def delete(self, absence_id):
        item = self.get_by_id(absence_id)
        if item is None:
            return False
        self.items.remove(item)
        return True


class FakeTeacherRepository:
    def __init__(self, teachers=None):
        self.items = list(teachers or [])

    def get_all(self):
        return list(self.items)

    def get_by_id(self, teacher_id):
        return next((item for item in self.items if item.id == teacher_id), None)

    def save(self, teacher):
        old = self.get_by_id(teacher.id)
        if old is None:
            self.items.append(teacher)
        else:
            self.items[self.items.index(old)] = teacher
        return teacher

    def delete(self, teacher_id):
        teacher = self.get_by_id(teacher_id)
        if teacher is None:
            return False
        self.items.remove(teacher)
        return True


class FakeScheduleRepository:
    def __init__(self, fixed=None, short=None, entries=None):
        self.fixed = fixed or {}
        self.short = short or {}
        self.entries = list(entries or [])

    def get_fixed_duty_teacher_ids(self, day, period):
        return list(self.fixed.get((day, period), []))

    def get_short_term_teacher_ids(self, day, period):
        return list(self.short.get((day, period), []))

    def get_all(self):
        return list(self.entries)

    def get_for_teacher(self, teacher_id):
        return [item for item in self.entries if item.teacher_id == teacher_id]

    def get_slot(self, teacher_id, day, period):
        return next((item for item in self.entries if item.teacher_id == teacher_id
                     and item.day_of_week == day and item.period == period), None)

    def save(self, entry):
        self.entries.append(entry)
        return entry

    def delete_for_teacher(self, teacher_id):
        self.entries = [item for item in self.entries if item.teacher_id != teacher_id]

    def delete_duties_for_teacher(self, teacher_id):
        self.fixed = {key: [value for value in values if value != teacher_id]
                      for key, values in self.fixed.items()}
        self.short = {key: [value for value in values if value != teacher_id]
                      for key, values in self.short.items()}


class FakeSubstitutionRepository:
    def __init__(self, logs=None):
        self.logs = list(logs or [])

    def get_all(self, date=None, substitute_teacher_id=None, absent_teacher_id=None):
        return [item for item in self.logs
                if (date is None or item.date == date)
                and (substitute_teacher_id is None or item.substitute_teacher_id == substitute_teacher_id)
                and (absent_teacher_id is None or item.absent_teacher_id == absent_teacher_id)]

    def save(self, log):
        self.logs.append(log)
        return log

    def get_busy_teacher_ids(self, date, period):
        return {item.substitute_teacher_id for item in self.logs
                if item.date == date and item.period == period}

    def get_intervention_counts(self):
        result = {}
        for item in self.logs:
            result[item.substitute_teacher_id] = result.get(item.substitute_teacher_id, 0) + 1
        return result

    def get_last_used_at(self, teacher_ids, period):
        return {teacher_id: max(
            (item.created_at for item in self.logs
             if item.substitute_teacher_id == teacher_id and item.period == period),
            default=datetime.min,
        ) for teacher_id in teacher_ids if any(
            item.substitute_teacher_id == teacher_id and item.period == period
            for item in self.logs
        )}


class FakeGroupRepository:
    def __init__(self, groups=None):
        self.items = list(groups or [])

    def get_all(self):
        return list(self.items)

    def get_by_id(self, group_id):
        return next((item for item in self.items if item.id == group_id), None)


@pytest.fixture
def fakes():
    return {
        "teachers": FakeTeacherRepository(),
        "absences": FakeAbsenceRepository(),
        "schedules": FakeScheduleRepository(),
        "substitutions": FakeSubstitutionRepository(),
        "groups": FakeGroupRepository(),
    }


@pytest.fixture
def teacher_factory():
    def make(name="Eva López", teacher_id="teacher-1"):
        return Teacher.create(name, teacher_id=teacher_id)
    return make


@pytest.fixture
def absence_factory():
    def make(teacher_id="teacher-1", date="2026-09-21", period=0):
        return Absence.create(teacher_id, date, period)
    return make
