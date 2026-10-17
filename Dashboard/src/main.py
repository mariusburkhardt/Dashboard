from pathlib import Path

from .storage import load_study_program
from .ui import load_data_path, print_dashboard


def main() -> int:
    base_path = Path(__file__).resolve().parent.parent
    data_path = load_data_path(base_path)
    program = load_study_program(data_path)
    if program is None:
        print(f"Daten konnten nicht geladen werden: {data_path}")
        return 1

    print_dashboard(program)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
