from __future__ import annotations

from dataclasses import dataclass, field

from .assessment import Assessment, AssessmentType


@dataclass
class Module:
    """Ein Studienmodul mit ECTS und genau einer Prüfungsleistung."""

    name: str
    ects: int = 5
    assessment: Assessment = field(
        default_factory=lambda: Assessment(AssessmentType.EXAM)
    )

    def __post_init__(self) -> None:
        """Prüft Modulnamen und ECTS-Wert."""
        if not self.name.strip():
            raise ValueError("Der Modulname darf nicht leer sein.")
        if type(self.ects) is not int or self.ects <= 0:
            raise ValueError(
                "Die ECTS-Punktzahl muss eine positive ganze Zahl sein."
            )
