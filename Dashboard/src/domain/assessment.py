from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class AssessmentType(Enum):
    """Mögliche Arten einer Prüfungsleistung."""

    EXAM = "Klausur"
    WORKBOOK = "Workbook"
    PORTFOLIO = "Portfolio"
    CASE_STUDY = "Fallstudie"
    PROJECT_REPORT = "Projektbericht"
    PROJECT_PRESENTATION = "Projektpräsentation"
    TERM_PAPER = "Hausarbeit"
    SEMINAR_PAPER = "Seminararbeit"


class AssessmentStatus(Enum):
    """Bearbeitungsstatus einer Prüfungsleistung."""

    OPEN = "Offen"
    IN_PROGRESS = "In Bearbeitung"
    PASSED = "Bestanden"
    FAILED = "Nicht bestanden"


@dataclass
class Assessment:
    """Prüfungsart, Status und Ergebnis eines Moduls."""

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
