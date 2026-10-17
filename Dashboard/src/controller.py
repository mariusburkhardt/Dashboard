from __future__ import annotations

from datetime import date

from .dashboard import DashboardService
from .dto import DashboardData
from .repositories import StudyProgramRepository


class DashboardController:
    """Koordiniert das Laden und Aufbereiten der Dashboard-Daten."""

    def __init__(
        self,
        dashboard_service: DashboardService,
        study_program_repository: StudyProgramRepository,
    ) -> None:
        """Übernimmt den Berechnungsdienst und das Studiengang-Repository."""
        self._dashboard_service = dashboard_service
        self._study_program_repository = study_program_repository

    def load_dashboard_data(self, today: date | None = None) -> DashboardData:
        """Lädt den Studiengang und liefert die berechneten Dashboard-Daten."""
        program = self._study_program_repository.load()
        if program is None:
            raise RuntimeError(
                "In der Datenbank ist kein Studiengang gespeichert."
            )
        return self._dashboard_service.build_dashboard_data(program, today)
