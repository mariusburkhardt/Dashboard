from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .semester import Semester


@dataclass
class StudyProgram:
    """Studiengang mit Stammdaten und den zugehörigen Semestern."""

    name: str
    start_date: date
    planned_semesters: int = 6
    required_ects: int = 180
    target_grade: float = 2.0
    student_name: str = "Studierende/r"
    semesters: list[Semester] = field(default_factory=list)
    def __post_init__(self) -> None:
        """Prüft Studiengangsnamen und Zielwerte."""
        if not self.name.strip():
            raise ValueError("Der Studiengangsname darf nicht leer sein.")
        if not self.student_name.strip():
            raise ValueError("Der Name der studierenden Person darf nicht leer sein.")
        if self.planned_semesters < 1:
            raise ValueError("Die geplante Semesterzahl muss positiv sein.")
        if type(self.required_ects) is not int or self.required_ects <= 0:
            raise ValueError("Die erforderliche ECTS-Punktzahl muss eine positive ganze Zahl sein.")
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
