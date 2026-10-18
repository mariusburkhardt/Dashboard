from __future__ import annotations

from datetime import date, timedelta

from .domain import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)


def create_sample_program(today: date | None = None) -> StudyProgram:
    """Erstellt gekennzeichnete Beispieldaten für den ersten Programmstart."""
    current_date = today or date.today()
    start_date = current_date - timedelta(days=184)
    first_semester_end = start_date + timedelta(days=181)
    second_semester_start = first_semester_end + timedelta(days=1)
    second_semester_end = second_semester_start + timedelta(days=181)
    passed_modules = [
        Module(
            name=name,
            assessment=Assessment(
                assessment_type=assessment_type,
                status=AssessmentStatus.PASSED,
                grade=grade,
            ),
        )
        for name, assessment_type, grade in [
            ("Einführung in die IT-Sicherheit", AssessmentType.EXAM, 1.7),
            ("Grundlagen der Informatik", AssessmentType.WORKBOOK, 2.0),
            ("Mathematik für Informatik", AssessmentType.EXAM, 2.3),
            ("Betriebssysteme", AssessmentType.PORTFOLIO, 1.7),
            ("Netzwerktechnik", AssessmentType.EXAM, 2.0),
            ("Programmierung mit Python", AssessmentType.PROJECT_REPORT, 1.3),
        ]
    ]
    return StudyProgram(
        name="Cyber Security B.Sc. (Beispieldaten)",
        start_date=start_date,
        student_name="Marius Burkhardt",
        semesters=[
            Semester(
                number=1,
                start_date=start_date,
                end_date=first_semester_end,
                modules=passed_modules,
            ),
            Semester(
                number=2,
                start_date=second_semester_start,
                end_date=second_semester_end,
                modules=[
                    Module(
                        name="Kryptographie",
                        assessment=Assessment(
                            AssessmentType.EXAM,
                            AssessmentStatus.IN_PROGRESS,
                        ),
                    ),
                    Module(
                        name="IT-Recht",
                        assessment=Assessment(AssessmentType.TERM_PAPER),
                    ),
                ],
            ),
        ],
    )
