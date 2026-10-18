from datetime import date

import pytest

from src.models import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)


def test_passed_assessment_requires_a_valid_grade() -> None:
    """Akzeptiert eine bestandene Prüfung mit gültiger Note."""
    assessment = Assessment(
        AssessmentType.EXAM,
        AssessmentStatus.PASSED,
        grade=1.7,
    )

    assert assessment.grade == 1.7


@pytest.mark.parametrize(
    ("status", "grade"),
    [
        (AssessmentStatus.OPEN, 2.0),
        (AssessmentStatus.IN_PROGRESS, 3.0),
        (AssessmentStatus.FAILED, 4.0),
        (AssessmentStatus.PASSED, None),
        (AssessmentStatus.PASSED, 4.1),
        (AssessmentStatus.PASSED, 0.9),
        (AssessmentStatus.PASSED, float("nan")),
        (AssessmentStatus.PASSED, float("inf")),
    ],
)
def test_assessment_rejects_invalid_grade_state(
    status: AssessmentStatus, grade: float | None
) -> None:
    """Lehnt nicht passende Status- und Notenkombinationen ab."""
    with pytest.raises(ValueError):
        Assessment(AssessmentType.EXAM, status, grade)


def test_module_defaults_to_five_ects_and_an_open_exam() -> None:
    """Verwendet für ein neues Modul die fachlichen Standardwerte."""
    module = Module("Kryptographie")

    assert module.ects == 5.0
    assert module.assessment.assessment_type is AssessmentType.EXAM
    assert module.assessment.status is AssessmentStatus.OPEN


def test_study_program_calculates_current_semester_from_start_date() -> None:
    """Berechnet den Semesterwechsel anhand des sechsmonatigen Zeitraums."""
    program = StudyProgram("Cyber Security", date(2026, 4, 17))

    assert program.current_semester(date(2026, 10, 16)) == 1
    assert program.current_semester(date(2026, 10, 17)) == 2


def test_semester_rejects_end_date_before_start_date() -> None:
    """Lehnt einen ungültigen Datumsbereich für ein Semester ab."""
    with pytest.raises(ValueError, match="darf nicht vor dem Start liegen"):
        Semester(
            number=1,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 9, 30),
        )


@pytest.mark.parametrize("ects", [0.0, -5.0, float("nan"), float("inf")])
def test_module_rejects_nonpositive_or_nonfinite_ects(ects: float) -> None:
    """Lehnt ungültige oder nicht endliche ECTS-Werte ab."""
    with pytest.raises(ValueError, match="ECTS-Punktzahl"):
        Module("Kryptographie", ects=ects)


@pytest.mark.parametrize(
    "required_ects", [0.0, -5.0, float("nan"), float("inf")]
)
def test_study_program_rejects_nonpositive_or_nonfinite_required_ects(
    required_ects: float,
) -> None:
    """Lehnt ungültige oder nicht endliche ECTS-Zielwerte ab."""
    with pytest.raises(ValueError, match="erforderliche ECTS-Punktzahl"):
        StudyProgram("Cyber Security", date(2026, 4, 17), required_ects=required_ects)
