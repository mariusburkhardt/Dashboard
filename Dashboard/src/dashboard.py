from typing import Dict, Optional

from .models import StudyProgram


def build_dashboard_summary(program: StudyProgram) -> Dict[str, Optional[float]]:
    return {
        "program_name": program.name,
        "required_ects": program.required_ects,
        "completed_ects": program.completed_ects(),
        "progress_percent": program.progress_percentage(),
        "current_average_grade": program.average_grade(),
        "target_grade": program.target_grade,
        "target_years": program.target_years,
    }


def is_target_on_track(program: StudyProgram) -> bool:
    average_grade = program.average_grade()
    return average_grade is not None and average_grade <= program.target_grade
