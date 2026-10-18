from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path

from .dashboard import DashboardService
from .dto import DashboardData
from .domain import Module, Semester, StudyProgram
from .repositories import StudyProgramRepository
from .transfer import export_study_program, import_study_program


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

    def load_study_program(self) -> StudyProgram:
        """Liefert den gespeicherten Studiengang für ein Bearbeitungsformular."""
        program = self._study_program_repository.load()
        if program is None:
            raise RuntimeError(
                "In der Datenbank ist kein Studiengang gespeichert."
            )
        return program

    def save_study_program(self, program: StudyProgram) -> None:
        """Speichert Änderungen an den Kerndaten des Studiengangs."""
        self._study_program_repository.save(program)

    def add_module(self, semester_number: int, module: Module) -> None:
        """Fügt einem vorhandenen Semester ein validiertes Modul hinzu."""
        program = self.load_study_program()
        semester = next(
            (
                item
                for item in program.semesters
                if item.number == semester_number
            ),
            None,
        )
        if semester is None:
            if program.semesters or semester_number != 1:
                raise ValueError(
                    f"Das Semester {semester_number} ist nicht vorhanden."
                )
            end_month_index = (
                program.start_date.year * 12
                + program.start_date.month
                - 1
                + 6
            )
            end_year, end_month_offset = divmod(end_month_index, 12)
            end_month = end_month_offset + 1
            end_day = min(
                program.start_date.day,
                monthrange(end_year, end_month)[1],
            )
            semester = Semester(
                number=1,
                start_date=program.start_date,
                end_date=date(end_year, end_month, end_day)
                - timedelta(days=1),
            )
            program.semesters.append(semester)
        semester.modules.append(module)
        self._study_program_repository.save(program)

    def import_study_program(self, path: Path) -> None:
        """Importiert einen Studiengang aus JSON und ersetzt den gespeicherten."""
        self._study_program_repository.save(import_study_program(path))

    def export_study_program(self, path: Path) -> None:
        """Exportiert den gespeicherten Studiengang als JSON."""
        export_study_program(self.load_study_program(), path)
