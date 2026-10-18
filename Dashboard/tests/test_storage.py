from datetime import date
from pathlib import Path
import sqlite3

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
    """Erstellt einen Studiengang mit einem bestandenen und offenen Modul."""
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


def test_save_and_load_study_program(tmp_path: Path) -> None:
    """Stellt einen Studiengang nach dem Speichern vollständig wieder her."""
    repository = SQLiteStudyProgramRepository(
        tmp_path / "data" / "study_dashboard.sqlite3"
    )
    program = make_program()

    repository.save(program)
    loaded = repository.load()

    assert loaded == program


def test_save_replaces_the_existing_program(tmp_path: Path) -> None:
    """Ersetzt den alten Bestand ohne verwaiste Semester oder Module."""
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


def test_load_returns_none_without_saved_program(tmp_path: Path) -> None:
    """Liefert bei einer leeren Datenbank keinen Studiengang."""
    repository = SQLiteStudyProgramRepository(
        tmp_path / "study_dashboard.sqlite3"
    )

    assert repository.load() is None


def test_existing_database_adds_default_student_name_column(
    tmp_path: Path,
) -> None:
    """Ergänzt bei älteren Datenbanken den Namen mit einem Standardwert."""
    database_path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE study_programs (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                planned_semesters INTEGER NOT NULL,
                required_ects REAL NOT NULL,
                target_grade REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO study_programs
                (id, name, start_date, planned_semesters, required_ects,
                 target_grade)
            VALUES (1, 'Cyber Security', '2026-04-17', 6, 180, 2.0)
            """
        )

    repository = SQLiteStudyProgramRepository(database_path)
    program = repository.load()

    assert program is not None
    assert program.student_name == "Studierende/r"
