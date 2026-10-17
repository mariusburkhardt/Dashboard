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


def test_passed_assessment_requires_a_valid_grade():
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
    ],
)
def test_assessment_rejects_invalid_grade_state(status, grade):
    with pytest.raises(ValueError):
        Assessment(AssessmentType.EXAM, status, grade)


def test_module_defaults_to_five_ects_and_an_open_exam():
    module = Module("Kryptographie")

    assert module.ects == 5.0
    assert module.assessment.assessment_type is AssessmentType.EXAM
    assert module.assessment.status is AssessmentStatus.OPEN


def test_study_program_calculates_current_semester_from_start_date():
    program = StudyProgram("Cyber Security", date(2026, 4, 17))

    assert program.current_semester(date(2026, 10, 16)) == 1
    assert program.current_semester(date(2026, 10, 17)) == 2


def test_semester_rejects_end_date_before_start_date():
    with pytest.raises(ValueError, match="cannot end before"):
        Semester(
            number=1,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 9, 30),
        )
