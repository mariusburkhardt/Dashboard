from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TargetStatus(Enum):
    """Ergebnis des Vergleichs eines Messwerts mit seinem Ziel."""

    ON_TRACK = "Im Ziel"
    BEHIND = "Hinter dem Ziel"
    NO_DATA = "Noch keine Daten"


class OverallStatus(Enum):
    """Zusammengefasster Status des Studienfortschritts."""

    ON_TRACK = "Im Plan"
    AT_RISK = "Aufmerksamkeit erforderlich"
    OVERDUE = "Geplante Studiendauer überschritten"


@dataclass(frozen=True)
class ModuleDashboardRow:
    """Für die Anzeige aufbereitete Daten eines Moduls."""

    semester_number: int
    module_name: str
    ects: int
    assessment_type: str
    assessment_status: str
    grade: float | None


@dataclass(frozen=True)
class DashboardData:
    """Typisierte Kennzahlen und Modulzeilen für die Dashboard-Ansicht."""

    program_name: str
    student_name: str
    current_semester: int
    planned_semesters: int
    remaining_semesters: int
    required_ects: int
    completed_ects: int
    progress_percentage: float
    expected_ects: int
    target_grade: float
    average_grade: float | None
    time_status: TargetStatus
    ects_status: TargetStatus
    grade_status: TargetStatus
    overall_status: OverallStatus
    modules: tuple[ModuleDashboardRow, ...]
