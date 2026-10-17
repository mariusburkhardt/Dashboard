from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TargetStatus(Enum):
    ON_TRACK = "Im Ziel"
    BEHIND = "Hinter dem Ziel"
    NO_DATA = "Noch keine Daten"


class OverallStatus(Enum):
    ON_TRACK = "Im Plan"
    AT_RISK = "Aufmerksamkeit erforderlich"
    OVERDUE = "Geplante Studiendauer überschritten"


@dataclass(frozen=True)
class ModuleDashboardRow:
    semester_number: int
    module_name: str
    ects: float
    assessment_type: str
    assessment_status: str
    grade: float | None


@dataclass(frozen=True)
class DashboardData:
    program_name: str
    current_semester: int
    planned_semesters: int
    remaining_semesters: int
    required_ects: float
    completed_ects: float
    progress_percentage: float
    expected_ects: float
    target_grade: float
    average_grade: float | None
    time_status: TargetStatus
    ects_status: TargetStatus
    grade_status: TargetStatus
    overall_status: OverallStatus
    modules: tuple[ModuleDashboardRow, ...]
