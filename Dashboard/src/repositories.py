from __future__ import annotations

from typing import Protocol

from .models import StudyProgram


class StudyProgramRepository(Protocol):
    def load(self) -> StudyProgram | None:
        """Load the saved study program, if one exists."""

    def save(self, program: StudyProgram) -> None:
        """Persist a complete study program."""
