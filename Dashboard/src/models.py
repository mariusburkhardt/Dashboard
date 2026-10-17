from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from math import isfinite


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
        """Prüft, ob Note und Prüfungsstatus zusammenpassen."""
        if self.grade is not None and self.status is not AssessmentStatus.PASSED:
            raise ValueError(
                "Eine Note kann nur bei bestandener Prüfungsleistung "
                "angegeben werden."
            )
        if self.status is AssessmentStatus.PASSED and self.grade is None:
            raise ValueError(
                "Für eine bestandene Prüfungsleistung muss eine Note "
                "angegeben werden."
            )
        if self.grade is not None and (
            not isfinite(self.grade) or not 1.0 <= self.grade <= 4.0
        ):
            raise ValueError("Eine bestandene Note muss zwischen 1,0 und 4,0 liegen.")


@dataclass
class Module:
    name: str
    ects: float = 5.0
    assessment: Assessment = field(
        default_factory=lambda: Assessment(AssessmentType.EXAM)
    )

    def __post_init__(self) -> None:
        """Prüft Modulnamen und ECTS-Wert."""
        if not self.name.strip():
            raise ValueError("Der Modulname darf nicht leer sein.")
        if not isfinite(self.ects) or self.ects <= 0:
            raise ValueError("Die ECTS-Punktzahl muss größer als null sein.")


@dataclass
class Semester:
    number: int
    start_date: date
    end_date: date
    modules: list[Module] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Prüft Semesternummer und Datumsbereich."""
        if self.number < 1:
            raise ValueError("Die Semesternummer muss positiv sein.")
        if self.end_date < self.start_date:
            raise ValueError("Das Semesterende darf nicht vor dem Start liegen.")


@dataclass
class StudyProgram:
    name: str
    start_date: date
    planned_semesters: int = 6
    required_ects: float = 180.0
    target_grade: float = 2.0
    semesters: list[Semester] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Prüft Studiengangsnamen und Zielwerte."""
        if not self.name.strip():
            raise ValueError("Der Studiengangsname darf nicht leer sein.")
        if self.planned_semesters < 1:
            raise ValueError("Die geplante Semesterzahl muss positiv sein.")
        if not isfinite(self.required_ects) or self.required_ects <= 0:
            raise ValueError("Die erforderliche ECTS-Punktzahl muss positiv sein.")
        if not 1.0 <= self.target_grade <= 4.0:
            raise ValueError("Die Zielnote muss zwischen 1,0 und 4,0 liegen.")

    def current_semester(self, today: date | None = None) -> int:
        """Berechnet anhand des Startdatums das aktuelle Sechsmonatssemester."""
        current_date = today or date.today()
        elapsed_months = (
            (current_date.year - self.start_date.year) * 12
            + current_date.month
            - self.start_date.month
        )
        if current_date.day < self.start_date.day:
            elapsed_months -= 1
        return max(1, elapsed_months // 6 + 1)
