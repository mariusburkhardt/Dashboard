from datetime import date
from pathlib import Path

import pytest

from src.domain import (
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


def test_example_study_program_can_be_imported() -> None:
    """Lädt den mitgelieferten Beispieldatensatz über den regulären JSON-Import."""
    example_path = (
        Path(__file__).parents[1]
        / "examples"
        / "beispielstudiengang.json"
    )

    program = import_study_program(example_path)

    assert program.name == "Cyber Security B.Sc"
    assert program.student_name == "Marius Burkhardt"
    assert program.required_ects == 180
    assert len(program.semesters) == 1
    assert sum(len(semester.modules) for semester in program.semesters) == 12


def test_import_converts_legacy_whole_number_ects_to_integers(
    tmp_path: Path,
) -> None:
    """Übernimmt alte JSON-ECTS als Fließkommazahl, sofern sie ganzzahlig ist."""
    path = tmp_path / "legacy.json"
    export_study_program(make_program(), path)
    path.write_text(
        path.read_text(encoding="utf-8")
        .replace('"ects": 5', '"ects": 5.0', 1)
        .replace('"required_ects": 180', '"required_ects": 180.0', 1),
        encoding="utf-8",
    )

    imported = import_study_program(path)

    assert type(imported.required_ects) is int
    assert type(imported.semesters[0].modules[0].ects) is int


def test_import_rejects_invalid_assessment_data(tmp_path: Path) -> None:
    """Lehnt eine bestandene Prüfungsleistung ohne Note beim Import ab."""
    path = tmp_path / "invalid.json"
    program = make_program()
    export_study_program(program, path)
    text = path.read_text(encoding="utf-8").replace('"grade": 1.7', '"grade": null')
    path.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match="Modul enthält fehlende oder ungültige"):
        import_study_program(path)


@pytest.mark.parametrize(
    ("old_value", "new_value"),
    [
        ('"ects": 5', '"ects": 5.5'),
        ('"ects": 5', '"ects": true'),
        ('"required_ects": 180', '"required_ects": 180.5'),
        ('"required_ects": 180', '"required_ects": true'),
    ],
)
def test_import_rejects_fractional_or_boolean_ects(
    tmp_path: Path, old_value: str, new_value: str
) -> None:
    """Lehnt gebrochene und boolesche ECTS-Werte im JSON-Import ab."""
    path = tmp_path / "invalid_ects.json"
    export_study_program(make_program(), path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(old_value, new_value, 1),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        import_study_program(path)
