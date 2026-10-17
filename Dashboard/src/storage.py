from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from .models import StudyProgram


def load_study_program(path: Path) -> Optional[StudyProgram]:
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return StudyProgram.from_dict(data)


def save_study_program(program: StudyProgram, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(program.to_dict(), handle, indent=2, ensure_ascii=False)
