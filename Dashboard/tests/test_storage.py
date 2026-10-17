from datetime import date
from pathlib import Path

from src.models import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)
from src.storage import SQLiteStudyProgramRepository


def make_program(name: str = "Cyber Security") -> StudyProgram:
    return StudyProgram(
        name=name,
        start_date=date(2026, 4, 17),
        semesters=[
            Semester(
                number=1,
                start_date=date(2026, 4, 17),
                end_date=date(2026, 10, 16),
                modules=[
                    Module(
                        "Kryptographie",
                        assessment=Assessment(
                            AssessmentType.EXAM,
                            AssessmentStatus.PASSED,
                            1.7,
                        ),
                    ),
                    Module("IT-Recht"),
                ],
            )
        ],
    )


def test_save_and_load_study_program(tmp_path: Path):
    repository = SQLiteStudyProgramRepository(
        tmp_path / "data" / "study_dashboard.sqlite3"
    )
    program = make_program()

    repository.save(program)
    loaded = repository.load()

    assert loaded == program


def test_save_replaces_the_existing_program(tmp_path: Path):
    repository = SQLiteStudyProgramRepository(
        tmp_path / "study_dashboard.sqlite3"
    )
    repository.save(make_program())
    repository.save(make_program("Updated program"))

    loaded = repository.load()

    assert loaded is not None
    assert loaded.name == "Updated program"
    assert len(loaded.semesters) == 1
    assert [module.name for module in loaded.semesters[0].modules] == [
        "Kryptographie",
        "IT-Recht",
    ]


def test_load_returns_none_without_saved_program(tmp_path: Path):
    repository = SQLiteStudyProgramRepository(
        tmp_path / "study_dashboard.sqlite3"
    )

    assert repository.load() is None
