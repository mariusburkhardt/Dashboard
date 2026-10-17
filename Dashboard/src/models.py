from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class AssessmentType(Enum):
    EXAM = "Klausur"
    WORKBOOK = "Workbook"
    PORTFOLIO = "Portfolio"
    CASE_STUDY = "Fallstudie"
    PROJECT_REPORT = "Projektbericht"
    PROJECT_PRESENTATION = "Projektpräsentation"
    TERM_PAPER = "Hausarbeit"
    SEMINAR_PAPER = "Seminararbeit"


class AssessmentStatus(Enum):
    OPEN = "Offen"
    IN_PROGRESS = "In Bearbeitung"
    PASSED = "Bestanden"
    FAILED = "Nicht bestanden"


@dataclass
class Assessment:
    assessment_type: AssessmentType
    status: AssessmentStatus = AssessmentStatus.OPEN
    grade: float | None = None

    def __post_init__(self) -> None:
        """Validate the grade against the assessment status."""
        if self.grade is not None and self.status is not AssessmentStatus.PASSED:
            raise ValueError("A grade can only be set for a passed assessment.")
        if self.status is AssessmentStatus.PASSED and self.grade is None:
            raise ValueError("A passed assessment must have a grade.")
        if self.grade is not None and not 1.0 <= self.grade <= 4.0:
            raise ValueError("A passing grade must be between 1.0 and 4.0.")


@dataclass
class Module:
    name: str
    ects: float = 5.0
    assessment: Assessment = field(
        default_factory=lambda: Assessment(AssessmentType.EXAM)
    )

    def __post_init__(self) -> None:
        """Validate the module name and its ECTS value."""
        if not self.name.strip():
            raise ValueError("A module name cannot be empty.")
        if self.ects <= 0:
            raise ValueError("ECTS must be greater than zero.")


@dataclass
class Semester:
    number: int
    start_date: date
    end_date: date
    modules: list[Module] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the semester number and date range."""
        if self.number < 1:
            raise ValueError("A semester number must be positive.")
        if self.end_date < self.start_date:
            raise ValueError("A semester cannot end before it starts.")


@dataclass
class StudyProgram:
    name: str
    start_date: date
    planned_semesters: int = 6
    required_ects: float = 180.0
    target_grade: float = 2.0
    semesters: list[Semester] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the study program's goals and identifying name."""
        if not self.name.strip():
            raise ValueError("A study program name cannot be empty.")
        if self.planned_semesters < 1:
            raise ValueError("The planned number of semesters must be positive.")
        if self.required_ects <= 0:
            raise ValueError("Required ECTS must be greater than zero.")
        if not 1.0 <= self.target_grade <= 4.0:
            raise ValueError("The target grade must be between 1.0 and 4.0.")

    def current_semester(self, today: date | None = None) -> int:
        """Calculate the current six-month semester from the start date."""
        current_date = today or date.today()
        elapsed_months = (
            (current_date.year - self.start_date.year) * 12
            + current_date.month
            - self.start_date.month
        )
        if current_date.day < self.start_date.day:
            elapsed_months -= 1
        return max(1, elapsed_months // 6 + 1)
