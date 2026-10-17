from pathlib import Path

from src.models import StudyProgram, Semester, Module
from src.storage import load_study_program, save_study_program


def test_save_and_load_study_program(tmp_path: Path):
    program = StudyProgram(
        name="Testprogramm",
        required_ects=30.0,
        semesters=[Semester(number=1, modules=[Module(code="TST101", name="Testmodul", ects=6.0, completed=True)])],
    )
    data_file = tmp_path / "study_data.json"
    save_study_program(program, data_file)

    loaded = load_study_program(data_file)
    assert loaded is not None
    assert loaded.name == "Testprogramm"
    assert loaded.required_ects == 30.0
    assert len(loaded.semesters) == 1
    assert loaded.semesters[0].modules[0].code == "TST101"
