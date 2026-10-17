import pytest

from src.models import Assessment, Module, Semester, StudyProgram


def test_assessment_completion():
    assessment = Assessment(name="Klausur", grade=1.3, passed=True)
    assert assessment.is_completed() is True


def test_module_average_grade():
    module = Module(
        code="BWL101",
        name="Einführung in die BWL",
        ects=6.0,
        assessments=[
            Assessment(name="Klausur", grade=1.7, passed=True),
            Assessment(name="Praktikum", grade=None, passed=False),
        ],
    )
    assert module.average_grade() == pytest.approx(1.7)


def test_semester_completed_ects():
    semester = Semester(
        number=1,
        modules=[
            Module(code="BWL101", name="Einführung in die BWL", ects=6.0, completed=True),
            Module(code="BWL102", name="Mathematik", ects=9.0, completed=False),
        ],
    )
    assert semester.completed_ects() == 6.0


def test_study_program_progress():
    program = StudyProgram(
        name="BWL",
        required_ects=180.0,
        semesters=[
            Semester(number=1, modules=[Module(code="BWL101", name="Einführung", ects=6.0, completed=True)]),
        ],
    )
    assert program.progress_percentage() == pytest.approx(3.3333333333333335)
