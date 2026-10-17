from __future__ import annotations

import tkinter as tk
from pathlib import Path

from .controller import DashboardController
from .dashboard import DashboardService
from .sample_data import create_sample_program
from .storage import SQLiteStudyProgramRepository
from .ui import DashboardView


class DashboardApplication:
    """Erzeugt und verbindet die Architekturkomponenten der Anwendung."""

    def __init__(self, database_path: Path | None = None) -> None:
        """Legt den Speicherort der Datenbank fest."""
        project_root = Path(__file__).resolve().parent.parent
        self._database_path = database_path or (
            project_root / "data" / "study_dashboard.sqlite3"
        )

    def start(self) -> None:
        """Initialisiert die Datenhaltung und startet die Benutzeroberfläche."""
        repository = SQLiteStudyProgramRepository(self._database_path)
        if repository.load() is None:
            repository.save(create_sample_program())

        controller = DashboardController(DashboardService(), repository)
        root = tk.Tk()
        DashboardView(root, controller).run()
