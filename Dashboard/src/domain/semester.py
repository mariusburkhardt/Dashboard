from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .module import Module


@dataclass
class Semester:
    """Studienabschnitt mit Datumsbereich und zugeordneten Modulen."""

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
