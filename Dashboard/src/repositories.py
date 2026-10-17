from __future__ import annotations

from typing import Protocol

from .models import StudyProgram


class StudyProgramRepository(Protocol):
    def load(self) -> StudyProgram | None:
        """Lädt den gespeicherten Studiengang, falls vorhanden."""

    def save(self, program: StudyProgram) -> None:
        """Speichert einen vollständigen Studiengang."""
