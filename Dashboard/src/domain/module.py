from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite

from .assessment import Assessment, AssessmentType


@dataclass
class Module:
    """Ein Studienmodul mit ECTS und genau einer Prüfungsleistung."""

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
