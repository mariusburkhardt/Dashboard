from __future__ import annotations

from datetime import date

from .dashboard import DashboardService
from .dto import DashboardData
from .repositories import StudyProgramRepository


class DashboardController:
    """Coordinate loading domain data and preparing dashboard information."""

    def __init__(
        self,
        dashboard_service: DashboardService,
        study_program_repository: StudyProgramRepository,
    ) -> None:
        self._dashboard_service = dashboard_service
        self._study_program_repository = study_program_repository

    def load_dashboard_data(self, today: date | None = None) -> DashboardData:
        """Load the study program and return its calculated dashboard data."""
        program = self._study_program_repository.load()
        if program is None:
            raise RuntimeError("No study program is saved in the database.")
        return self._dashboard_service.build_dashboard_data(program, today)
