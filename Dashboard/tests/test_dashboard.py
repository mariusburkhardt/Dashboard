from datetime import date
from pathlib import Path

import pytest

from src.controller import DashboardController
from src.dashboard import DashboardService
from src.dto import OverallStatus, TargetStatus
from src.models import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)
from src.storage import SQLiteStudyProgramRepository


def make_program() -> StudyProgram:
    """Erstellt einen Studiengang mit bestandenen Beispielmodulen."""
    passed_modules = [
        Module(
            f"Modul {number}",
            assessment=Assessment(
                AssessmentType.EXAM,
                AssessmentStatus.PASSED,
                grade,
            ),
        )
        for number, grade in enumerate(
            [1.7, 2.0, 2.3, 1.7, 2.0, 1.3], start=1
        )
    ]
    return StudyProgram(
        name="Cyber Security",
        start_date=date(2026, 4, 17),
        semesters=[
            Semester(
                number=1,
                start_date=date(2026, 4, 17),
                end_date=date(2026, 10, 16),
                modules=passed_modules,
            )
        ],
    )


def test_dashboard_service_calculates_targets_and_average() -> None:
    """Berechnet ECTS-, Zeit- und Notenziele für einen Studiengang."""
    data = DashboardService().build_dashboard_data(
        make_program(), today=date(2026, 10, 17)
    )

    assert data.current_semester == 2
    assert data.remaining_semesters == 4
    assert data.completed_ects == 30
    assert data.expected_ects == 30
    assert data.progress_percentage == pytest.approx(100 * 30 / 180)
    assert data.average_grade == pytest.approx(11 / 6)
    assert data.ects_status is TargetStatus.ON_TRACK
    assert data.grade_status is TargetStatus.ON_TRACK
    assert data.overall_status is OverallStatus.ON_TRACK
    assert len(data.modules) == 6


def test_controller_reports_missing_saved_program() -> None:
    """Meldet verständlich, wenn kein Studiengang gespeichert wurde."""
    class EmptyRepository:
        """Repository-Stub ohne gespeicherte Daten."""

        def load(self) -> StudyProgram | None:
            """Liefert keinen gespeicherten Studiengang."""
            return None

        def save(self, program: StudyProgram) -> None:
            """Löst einen Fehler aus, da im Test nichts gespeichert werden soll."""
            raise AssertionError(
                "Speichern soll in diesem Test nicht aufgerufen werden."
            )

    controller = DashboardController(DashboardService(), EmptyRepository())

    with pytest.raises(RuntimeError, match="kein Studiengang"):
        controller.load_dashboard_data()


def test_controller_adds_module_and_creates_first_semester_if_needed(
    tmp_path: Path,
) -> None:
    """Erstellt das erste Semester bei Bedarf und speichert ein neues Modul."""
    repository = SQLiteStudyProgramRepository(tmp_path / "dashboard.sqlite3")
    program = StudyProgram("Cyber Security", date(2026, 1, 31))
    repository.save(program)
    controller = DashboardController(DashboardService(), repository)

    controller.add_module(1, Module("Kryptographie"))

    loaded = repository.load()
    assert loaded is not None
    assert loaded.semesters[0].start_date == date(2026, 1, 31)
    assert loaded.semesters[0].end_date == date(2026, 7, 30)
    assert loaded.semesters[0].modules[0].name == "Kryptographie"
