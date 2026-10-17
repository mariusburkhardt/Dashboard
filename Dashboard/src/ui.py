from pathlib import Path
from typing import Dict

from .dashboard import build_dashboard_summary, is_target_on_track
from .models import StudyProgram


def render_summary(summary: Dict[str, float], program: StudyProgram) -> str:
    return (
        f"Studiengang: {summary['program_name']}\n"
        f"Ziel-ECTS: {summary['required_ects']}\n"
        f"Erreichte ECTS: {summary['completed_ects']}\n"
        f"Fortschritt: {summary['progress_percent']:.1f}%\n"
        f"Aktuelle Durchschnittsnote: {summary['current_average_grade'] or 'n/a'}\n"
        f"Zielnote: {summary['target_grade']}\n"
        f"Zieljahr: {summary['target_years']}\n"
        f"Auf Kurs: {'Ja' if is_target_on_track(program) else 'Nein'}\n"
    )


def print_dashboard(program: StudyProgram) -> None:
    summary = build_dashboard_summary(program)
    print(render_summary(summary, program))


def load_data_path(base_path: Path) -> Path:
    return base_path / "data" / "study_data.json"
