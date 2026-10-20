from collections.abc import Callable
from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.application import DashboardApplication
from src.controller import DashboardController
from src.dashboard import DashboardService
from src.dto import OverallStatus, TargetStatus
from src.domain import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)
from src.storage import SQLiteStudyProgramRepository
from src.ui import DashboardView


def make_program() -> StudyProgram:
    """Erstellt einen Studiengang mit bestandenen Beispielmodulen."""
    passed_modules = [
        Module(
            f"Modul {number}",
            assessment=Assessment(
                AssessmentType.EXAM,
                AssessmentStatus.PASSED,
                grade,
            ),
        )
        for number, grade in enumerate(
            [1.7, 2.0, 2.3, 1.7, 2.0, 1.3], start=1
        )
    ]
    return StudyProgram(
        name="Cyber Security",
        start_date=date(2026, 4, 17),
        semesters=[
            Semester(
                number=1,
                start_date=date(2026, 4, 17),
                end_date=date(2026, 10, 16),
                modules=passed_modules,
            )
        ],
    )


def test_dashboard_service_calculates_targets_and_average() -> None:
    """Berechnet ECTS-, Zeit- und Notenziele für einen Studiengang."""
    data = DashboardService().build_dashboard_data(
        make_program(), today=date(2026, 10, 17)
    )

    assert data.current_semester == 2
    assert data.remaining_semesters == 4
    assert data.completed_ects == 30
    assert data.expected_ects == 30
    assert data.progress_percentage == pytest.approx(100 * 30 / 180)
    assert data.average_grade == pytest.approx(11 / 6)
    assert data.ects_status is TargetStatus.ON_TRACK
    assert data.grade_status is TargetStatus.ON_TRACK
    assert data.overall_status is OverallStatus.ON_TRACK
    assert len(data.modules) == 6


def test_dashboard_rounds_expected_ects_up_to_next_whole_point() -> None:
    """Rundet ein zeitanteiliges ECTS-Soll auf ganze Punkte auf."""
    program = StudyProgram(
        "Cyber Security",
        date(2026, 4, 17),
        planned_semesters=6,
        required_ects=181,
    )

    data = DashboardService().build_dashboard_data(
        program, today=date(2026, 10, 17)
    )

    assert data.expected_ects == 31
    assert isinstance(data.expected_ects, int)


def test_controller_returns_none_without_saved_program() -> None:
    """Liefert bei einer leeren Datenbank keinen Studiengang."""
    class EmptyRepository:
        """Repository-Stub ohne gespeicherte Daten."""

        def load(self) -> StudyProgram | None:
            """Liefert keinen gespeicherten Studiengang."""
            return None

        def save(self, program: StudyProgram) -> None:
            """Löst einen Fehler aus, da im Test nichts gespeichert werden soll."""
            raise AssertionError(
                "Speichern soll in diesem Test nicht aufgerufen werden."
            )

    controller = DashboardController(DashboardService(), EmptyRepository())

    assert controller.load_study_program() is None
    with pytest.raises(RuntimeError, match="kein Studiengang"):
        controller.load_dashboard_data()


def test_first_application_start_keeps_database_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Erstellt beim ersten Programmstart keinen Beispielstudiengang."""
    class InertDashboardView:
        """Überspringt die GUI-Ereignisschleife im Anwendungstest."""

        def __init__(self, root: object, controller: DashboardController) -> None:
            """Akzeptiert die Anwendungsabhängigkeiten ohne GUI-Aufbau."""

        def run(self) -> None:
            """Beendet den Testlauf unmittelbar."""

    monkeypatch.setattr("src.application.tk.Tk", lambda: None)
    monkeypatch.setattr("src.application.DashboardView", InertDashboardView)
    database_path = tmp_path / "empty.sqlite3"

    DashboardApplication(database_path).start()

    assert SQLiteStudyProgramRepository(database_path).load() is None


def test_empty_dashboard_prompts_for_core_data() -> None:
    """Zeigt den Anpassungshinweis in allen leeren Kerndatenfeldern."""
    view = object.__new__(DashboardView)
    widget_names = (
        "_profile_name",
        "_profile_program",
        "_profile_start",
        "_profile_plan",
        "_profile_goal",
        "_profile_ects",
        "_core_data_button",
        "_add_module_button",
        "_edit_module_button",
        "_average_grade",
        "_grade_target",
        "_time_label",
        "_ects_label",
        "_grade_badge",
        "_overall_badge",
        "_time_bar",
        "_ects_bar",
        "_avatar",
        "_module_table",
    )
    for name in widget_names:
        setattr(view, name, Mock())
    view._avatar_text_id = 1
    view._module_table.get_children.return_value = ()
    view._time_bar.winfo_width.return_value = 100
    view._ects_bar.winfo_width.return_value = 100

    view._display_empty_state()

    prompt = "Kerndaten anpassen"
    for name in (
        "_profile_name",
        "_profile_program",
        "_core_data_button",
    ):
        assert getattr(view, name).configure.call_args.kwargs["text"] == prompt
    assert view._profile_start.configure.call_args.kwargs["text"].endswith(prompt)
    assert view._profile_plan.configure.call_args.kwargs["text"].endswith(prompt)
    assert view._profile_goal.configure.call_args.kwargs["text"].endswith(prompt)
    assert view._profile_ects.configure.call_args.kwargs["text"].endswith(prompt)
    assert view._add_module_button.configure.call_args.kwargs["state"] == "disabled"
    assert view._edit_module_button.configure.call_args.kwargs["state"] == "disabled"


def test_progress_display_shows_overall_status_and_remaining_semesters() -> None:
    """Zeigt Gesamtstatus und verbleibende Semester in der Fortschrittsansicht."""
    view = object.__new__(DashboardView)
    for name in (
        "_average_grade",
        "_grade_target",
        "_overall_badge",
        "_grade_badge",
        "_time_label",
        "_time_bar",
        "_ects_label",
        "_ects_bar",
    ):
        setattr(view, name, Mock())
    view._set_overall_badge = Mock()
    view._set_badge = Mock()
    view._set_progress_bar = Mock()

    data = DashboardService().build_dashboard_data(
        make_program(), today=date(2026, 10, 17)
    )
    view._display_progress(data)

    view._set_overall_badge.assert_called_once_with(OverallStatus.ON_TRACK)
    view._set_badge.assert_called_once_with(
        view._grade_badge, TargetStatus.ON_TRACK
    )
    assert "4 verbleibend" in view._time_label.configure.call_args.kwargs["text"]


@pytest.mark.parametrize(
    ("status", "label", "color"),
    [
        (OverallStatus.ON_TRACK, "Im Plan", "#2C9B73"),
        (OverallStatus.AT_RISK, "Aufmerksamkeit erforderlich", "#D18B25"),
        (
            OverallStatus.OVERDUE,
            "Studiendauer überschritten",
            "#C34D4D",
        ),
    ],
)
def test_overall_status_badge_uses_the_aggregate_status_color(
    status: OverallStatus, label: str, color: str
) -> None:
    """Zeigt den Gesamtstatus mit passender Beschriftung und Ampelfarbe."""
    view = object.__new__(DashboardView)
    view._overall_badge = Mock()

    view._set_overall_badge(status)

    view._overall_badge.configure.assert_called_once_with(
        text=label, bg=color, fg=DashboardView._COLORS["white"]
    )


@pytest.mark.parametrize(
    ("assessment_status", "label", "tag"),
    [
        (AssessmentStatus.OPEN, "Geplant", "planned"),
        (AssessmentStatus.IN_PROGRESS, "In Bearbeitung", "in_progress"),
        (AssessmentStatus.PASSED, "Abgeschlossen", "passed"),
        (AssessmentStatus.FAILED, "Nicht bestanden", "failed"),
    ],
)
def test_module_table_applies_status_colors(
    assessment_status: AssessmentStatus, label: str, tag: str
) -> None:
    """Ordnet jedem Prüfungsstatus die passende farbige Tabellenmarkierung zu."""
    data = DashboardService().build_dashboard_data(
        make_program(), today=date(2026, 10, 17)
    )
    module = replace(
        data.modules[0],
        assessment_status=assessment_status.value,
        grade=1.7 if assessment_status is AssessmentStatus.PASSED else None,
    )
    data = replace(data, modules=(module,))
    view = object.__new__(DashboardView)
    view._module_table = Mock()
    view._module_table.get_children.return_value = ()
    view._module_locations = {}
    view._update_edit_module_button = Mock()

    view._display_modules(data)

    inserted_row = view._module_table.insert.call_args.kwargs
    assert inserted_row["values"][-1] == label
    assert inserted_row["tags"] == (tag,)


def test_core_data_dialog_creates_first_study_program() -> None:
    """Speichert beim ersten Ausfüllen einen neuen Studiengang."""
    view = object.__new__(DashboardView)
    view._controller = Mock()
    view._controller.load_study_program.return_value = None
    dialog = Mock()
    values = [
        "Beispielperson",
        "Cyber Security",
        "2026-04-17",
        "6",
        "180",
        "2,0",
    ]
    entries = [Mock() for _ in values]
    for entry, value in zip(entries, values):
        entry.get.return_value = value
    view._form_dialog = Mock(return_value=(dialog, entries))
    callbacks: list[Callable[[], None]] = []
    view._form_buttons = Mock(
        side_effect=lambda _dialog, save: callbacks.append(save)
    )
    view._refresh = Mock()

    view._open_core_data_dialog()
    callbacks[0]()

    saved_program = view._controller.save_study_program.call_args.args[0]
    assert saved_program.name == "Cyber Security"
    assert saved_program.student_name == "Beispielperson"
    assert saved_program.required_ects == 180
    assert view._form_dialog.call_args.args[0] == "Kerndaten anpassen"
    dialog.destroy.assert_called_once_with()
    view._refresh.assert_called_once_with()


def test_controller_adds_module_and_creates_first_semester_if_needed(
    tmp_path: Path,
) -> None:
    """Erstellt das erste Semester bei Bedarf und speichert ein neues Modul."""
    repository = SQLiteStudyProgramRepository(tmp_path / "dashboard.sqlite3")
    program = StudyProgram("Cyber Security", date(2026, 1, 31))
    repository.save(program)
    controller = DashboardController(DashboardService(), repository)

    controller.add_module(1, Module("Kryptographie"))

    loaded = repository.load()
    assert loaded is not None
    assert loaded.semesters[0].start_date == date(2026, 1, 31)
    assert loaded.semesters[0].end_date == date(2026, 7, 30)
    assert loaded.semesters[0].modules[0].name == "Kryptographie"


def test_controller_updates_module_assessment_and_persists_it(
    tmp_path: Path,
) -> None:
    """Aktualisiert eine Prüfungsleistung am ausgewählten Modul."""
    repository = SQLiteStudyProgramRepository(tmp_path / "dashboard.sqlite3")
    program = make_program()
    repository.save(program)
    controller = DashboardController(DashboardService(), repository)
    updated_module = Module(
        "Modul 1",
        ects=5,
        assessment=Assessment(
            AssessmentType.EXAM,
            AssessmentStatus.PASSED,
            grade=1.3,
        ),
    )

    controller.update_module(1, 0, updated_module)

    loaded = repository.load()
    assert loaded is not None
    assert loaded.semesters[0].modules[0] == updated_module
    assert loaded.semesters[0].modules[0].assessment.grade == 1.3
    assert loaded.semesters[0].modules[1] == program.semesters[0].modules[1]


def test_controller_rejects_missing_module_position(tmp_path: Path) -> None:
    """Lehnt eine ungültige Modulposition beim Aktualisieren ab."""
    repository = SQLiteStudyProgramRepository(tmp_path / "dashboard.sqlite3")
    repository.save(make_program())
    controller = DashboardController(DashboardService(), repository)

    with pytest.raises(ValueError, match="Modul ist nicht mehr vorhanden"):
        controller.update_module(1, 99, Module("Neues Modul"))
