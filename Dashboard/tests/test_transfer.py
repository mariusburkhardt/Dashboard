from datetime import date
from pathlib import Path

import pytest

from src.models import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)
from src.transfer import export_study_program, import_study_program


def make_program() -> StudyProgram:
    """Erstellt einen Studiengang mit einer bestandenen Prüfungsleistung."""
    return StudyProgram(
        name="Cyber Security",
        student_name="Marius Burkhardt",
        start_date=date(2026, 4, 17),
        semesters=[
            Semester(
                number=1,
                start_date=date(2026, 4, 17),
                end_date=date(2026, 10, 16),
                modules=[
                    Module(
                        "Kryptographie",
                        assessment=Assessment(
                            AssessmentType.EXAM,
                            AssessmentStatus.PASSED,
                            1.7,
                        ),
                    )
                ],
            )
        ],
    )


def test_export_and_import_preserve_the_study_program(
    tmp_path: Path,
) -> None:
    """Erhält Kerndaten, Semester, Module und Prüfungsnoten im JSON-Transfer."""
    path = tmp_path / "backup.json"
    program = make_program()

    export_study_program(program, path)

    assert import_study_program(path) == program


def test_import_rejects_unsupported_format_version(tmp_path: Path) -> None:
    """Lehnt JSON-Dateien mit unbekannter Formatversion verständlich ab."""
    path = tmp_path / "unsupported.json"
    path.write_text('{"format_version": 2}', encoding="utf-8")

    with pytest.raises(ValueError, match="Dateiversion wird nicht unterstützt"):
        import_study_program(path)


def test_import_rejects_invalid_assessment_data(tmp_path: Path) -> None:
    """Lehnt eine bestandene Prüfungsleistung ohne Note beim Import ab."""
    path = tmp_path / "invalid.json"
    program = make_program()
    export_study_program(program, path)
    text = path.read_text(encoding="utf-8").replace('"grade": 1.7', '"grade": null')
    path.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match="Modul enthält fehlende oder ungültige"):
        import_study_program(path)
