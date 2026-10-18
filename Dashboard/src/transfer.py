from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .domain import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)


def export_study_program(program: StudyProgram, path: Path) -> None:
    """Exportiert einen Studiengang als JSON-Datei."""
    data = {
        "format_version": 1,
        "name": program.name,
        "student_name": program.student_name,
        "start_date": program.start_date.isoformat(),
        "planned_semesters": program.planned_semesters,
        "required_ects": program.required_ects,
        "target_grade": program.target_grade,
        "semesters": [
            {
                "number": semester.number,
                "start_date": semester.start_date.isoformat(),
                "end_date": semester.end_date.isoformat(),
                "modules": [
                    {
                        "name": module.name,
                        "ects": module.ects,
                        "assessment_type": (
                            module.assessment.assessment_type.name
                        ),
                        "assessment_status": module.assessment.status.name,
                        "grade": module.assessment.grade,
                    }
                    for module in semester.modules
                ],
            }
            for semester in program.semesters
        ],
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False, allow_nan=False)


def import_study_program(path: Path) -> StudyProgram:
    """Liest einen Studiengang aus einer JSON-Datei und validiert seine Daten."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return _study_program_from_data(data)


def _study_program_from_data(data: Any) -> StudyProgram:
    """Wandelt JSON-Daten in ein validiertes Studiengangsmodell um."""
    if not isinstance(data, dict):
        raise ValueError("Die JSON-Datei muss ein Objekt enthalten.")
    if data.get("format_version") != 1:
        raise ValueError("Die JSON-Dateiversion wird nicht unterstützt.")

    semesters_data = data.get("semesters")
    if not isinstance(semesters_data, list):
        raise ValueError("Die JSON-Datei enthält keine gültige Semesterliste.")

    semesters = []
    for semester_data in semesters_data:
        if not isinstance(semester_data, dict):
            raise ValueError("Ein Semestereintrag ist ungültig.")
        modules_data = semester_data.get("modules")
        if not isinstance(modules_data, list):
            raise ValueError("Ein Semester enthält keine gültige Modulliste.")
        modules = []
        for module_data in modules_data:
            if not isinstance(module_data, dict):
                raise ValueError("Ein Moduleintrag ist ungültig.")
            try:
                assessment = Assessment(
                    assessment_type=AssessmentType[module_data["assessment_type"]],
                    status=AssessmentStatus[module_data["assessment_status"]],
                    grade=module_data["grade"],
                )
                modules.append(
                    Module(
                        name=module_data["name"],
                        ects=module_data["ects"],
                        assessment=assessment,
                    )
                )
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    "Ein Modul enthält fehlende oder ungültige Pflichtfelder."
                ) from error

        try:
            semesters.append(
                Semester(
                    number=semester_data["number"],
                    start_date=date.fromisoformat(semester_data["start_date"]),
                    end_date=date.fromisoformat(semester_data["end_date"]),
                    modules=modules,
                )
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                "Ein Semester enthält ungültige oder fehlende Pflichtfelder."
            ) from error

    try:
        return StudyProgram(
            name=data["name"],
            student_name=data["student_name"],
            start_date=date.fromisoformat(data["start_date"]),
            planned_semesters=data["planned_semesters"],
            required_ects=data["required_ects"],
            target_grade=data["target_grade"],
            semesters=semesters,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "Die JSON-Datei enthält ungültige oder fehlende Studiengangsdaten."
        ) from error
