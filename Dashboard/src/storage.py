from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from .domain import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    Semester,
    StudyProgram,
)
from .repositories import StudyProgramRepository


class SQLiteStudyProgramRepository:
    """Speichert Studiengänge und zugehörige Fachobjekte in SQLite."""

    def __init__(self, database_path: Path) -> None:
        """Legt den Datenbankpfad fest und erstellt das Tabellenschema."""
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_schema()

    def load(self) -> StudyProgram | None:
        """Lädt den gespeicherten Studiengang samt zugehöriger Objekte."""
        with closing(sqlite3.connect(self._database_path)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            program_row = connection.execute(
                """
                SELECT name, start_date, planned_semesters, required_ects,
                       target_grade, student_name
                FROM study_programs
                WHERE id = 1
                """
            ).fetchone()
            if program_row is None:
                return None

            semesters = []
            semester_rows = connection.execute(
                """
                SELECT id, number, start_date, end_date
                FROM semesters
                WHERE program_id = 1
                ORDER BY number
                """
            ).fetchall()
            for semester_row in semester_rows:
                modules = []
                module_rows = connection.execute(
                    """
                    SELECT id, name, ects
                    FROM modules
                    WHERE semester_id = ?
                    ORDER BY id
                    """,
                    (semester_row["id"],),
                ).fetchall()
                for module_row in module_rows:
                    assessment_row = connection.execute(
                        """
                        SELECT assessment_type, status, grade
                        FROM assessments
                        WHERE module_id = ?
                        """,
                        (module_row["id"],),
                    ).fetchone()
                    if assessment_row is None:
                        raise ValueError(
                            f"Zum Modul {module_row['name']!r} fehlt eine "
                            "Prüfungsleistung."
                        )
                    modules.append(
                        Module(
                            name=module_row["name"],
                            ects=module_row["ects"],
                            assessment=Assessment(
                                assessment_type=AssessmentType(
                                    assessment_row["assessment_type"]
                                ),
                                status=AssessmentStatus(assessment_row["status"]),
                                grade=assessment_row["grade"],
                            ),
                        )
                    )
                semesters.append(
                    Semester(
                        number=semester_row["number"],
                        start_date=date.fromisoformat(semester_row["start_date"]),
                        end_date=date.fromisoformat(semester_row["end_date"]),
                        modules=modules,
                    )
                )
            return StudyProgram(
                name=program_row["name"],
                start_date=date.fromisoformat(program_row["start_date"]),
                planned_semesters=program_row["planned_semesters"],
                required_ects=program_row["required_ects"],
                target_grade=program_row["target_grade"],
                student_name=program_row["student_name"],
                semesters=semesters,
            )

    def save(self, program: StudyProgram) -> None:
        """Ersetzt den gespeicherten Studiengang in einer Transaktion."""
        with closing(sqlite3.connect(self._database_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                connection.execute("DELETE FROM study_programs WHERE id = 1")
                connection.execute(
                    """
                    INSERT INTO study_programs (
                        id, name, start_date, planned_semesters,
                        required_ects, target_grade, student_name
                    )
                    VALUES (1, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        program.name,
                        program.start_date.isoformat(),
                        program.planned_semesters,
                        program.required_ects,
                        program.target_grade,
                        program.student_name,
                    ),
                )
                for semester in program.semesters:
                    semester_cursor = connection.execute(
                        """
                        INSERT INTO semesters (
                            program_id, number, start_date, end_date
                        )
                        VALUES (1, ?, ?, ?)
                        """,
                        (
                            semester.number,
                            semester.start_date.isoformat(),
                            semester.end_date.isoformat(),
                        ),
                    )
                    semester_id = semester_cursor.lastrowid
                    if semester_id is None:
                        raise RuntimeError(
                            "SQLite hat keine Semester-ID zurückgegeben."
                        )
                    for module in semester.modules:
                        module_cursor = connection.execute(
                            """
                            INSERT INTO modules (semester_id, name, ects)
                            VALUES (?, ?, ?)
                            """,
                            (semester_id, module.name, module.ects),
                        )
                        module_id = module_cursor.lastrowid
                        if module_id is None:
                            raise RuntimeError(
                                "SQLite hat keine Modul-ID zurückgegeben."
                            )
                        connection.execute(
                            """
                            INSERT INTO assessments (
                                module_id, assessment_type, status, grade
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                module_id,
                                module.assessment.assessment_type.value,
                                module.assessment.status.value,
                                module.assessment.grade,
                            ),
                        )

    def _create_schema(self) -> None:
        """Erstellt die SQLite-Tabellen, falls sie noch nicht vorhanden sind."""
        with closing(sqlite3.connect(self._database_path)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = OFF")
            with connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS study_programs (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        name TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        planned_semesters INTEGER NOT NULL CHECK (
                            planned_semesters > 0
                        ),
                        required_ects INTEGER NOT NULL CHECK (
                            required_ects > 0
                            AND typeof(required_ects) = 'integer'
                        ),
                        target_grade REAL NOT NULL CHECK (
                            target_grade BETWEEN 1.0 AND 4.0
                        ),
                        student_name TEXT NOT NULL DEFAULT 'Studierende/r'
                    );
                    CREATE TABLE IF NOT EXISTS semesters (
                        id INTEGER PRIMARY KEY,
                        program_id INTEGER NOT NULL REFERENCES study_programs(id)
                            ON DELETE CASCADE,
                        number INTEGER NOT NULL CHECK (number > 0),
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        UNIQUE (program_id, number)
                    );
                    CREATE TABLE IF NOT EXISTS modules (
                        id INTEGER PRIMARY KEY,
                        semester_id INTEGER NOT NULL REFERENCES semesters(id)
                            ON DELETE CASCADE,
                        name TEXT NOT NULL,
                        ects INTEGER NOT NULL CHECK (
                            ects > 0 AND typeof(ects) = 'integer'
                        )
                    );
                    CREATE TABLE IF NOT EXISTS assessments (
                        id INTEGER PRIMARY KEY,
                        module_id INTEGER NOT NULL UNIQUE REFERENCES modules(id)
                            ON DELETE CASCADE,
                        assessment_type TEXT NOT NULL,
                        status TEXT NOT NULL CHECK (
                            status IN (
                                'Offen', 'In Bearbeitung',
                                'Bestanden', 'Nicht bestanden'
                            )
                        ),
                        grade REAL,
                        CHECK (
                            (
                                status = 'Bestanden'
                                AND grade IS NOT NULL
                                AND grade BETWEEN 1.0 AND 4.0
                            )
                            OR (status != 'Bestanden' AND grade IS NULL)
                        ),
                        CHECK (
                            assessment_type IN (
                                'Klausur', 'Workbook', 'Portfolio',
                                'Fallstudie', 'Projektbericht',
                                'Projektpräsentation', 'Hausarbeit',
                                'Seminararbeit'
                            )
                        )
                    );
                    """
                )
                columns = {
                    row["name"]
                    for row in connection.execute(
                        "PRAGMA table_info(study_programs)"
                    )
                }
                if "student_name" not in columns:
                    connection.execute(
                        """
                        ALTER TABLE study_programs
                        ADD COLUMN student_name TEXT NOT NULL
                        DEFAULT 'Studierende/r'
                        """
                    )
                self._migrate_ects_columns(connection)
            connection.execute("PRAGMA foreign_keys = ON")

    @staticmethod
    def _migrate_ects_columns(connection: sqlite3.Connection) -> None:
        """Migriert ganzzahlige ECTS-Spalten und erhält bestehende Einträge."""
        migrations = (
            (
                "study_programs",
                "required_ects",
                """
                CREATE TABLE study_programs_integer_migration (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    planned_semesters INTEGER NOT NULL CHECK (
                        planned_semesters > 0
                    ),
                    required_ects INTEGER NOT NULL CHECK (
                        required_ects > 0
                        AND typeof(required_ects) = 'integer'
                    ),
                    target_grade REAL NOT NULL CHECK (
                        target_grade BETWEEN 1.0 AND 4.0
                    ),
                    student_name TEXT NOT NULL DEFAULT 'Studierende/r'
                )
                """,
                """
                INSERT INTO study_programs_integer_migration (
                    id, name, start_date, planned_semesters, required_ects,
                    target_grade, student_name
                )
                SELECT id, name, start_date, planned_semesters,
                       CAST(required_ects AS INTEGER), target_grade,
                       student_name
                FROM study_programs
                """,
                "study_programs",
            ),
            (
                "modules",
                "ects",
                """
                CREATE TABLE modules_integer_migration (
                    id INTEGER PRIMARY KEY,
                    semester_id INTEGER NOT NULL REFERENCES semesters(id)
                        ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    ects INTEGER NOT NULL CHECK (
                        ects > 0 AND typeof(ects) = 'integer'
                    )
                )
                """,
                """
                INSERT INTO modules_integer_migration (
                    id, semester_id, name, ects
                )
                SELECT id, semester_id, name, CAST(ects AS INTEGER)
                FROM modules
                """,
                "modules",
            ),
        )
        pending_migrations = []
        for table, column, create_sql, copy_sql, _ in migrations:
            column_types = {
                row["name"]: row["type"].upper()
                for row in connection.execute(f"PRAGMA table_info({table})")
            }
            if column_types[column] == "INTEGER":
                continue
            fractional_values = connection.execute(
                f"""
                SELECT COUNT(*) FROM {table}
                WHERE {column} IS NULL OR {column} <= 0
                   OR {column} != CAST({column} AS INTEGER)
                """
            ).fetchone()[0]
            if fractional_values:
                raise ValueError(
                    f"Die Datenbank enthält ungültige oder gebrochene Werte "
                    f"für {column}; die ECTS-Migration wurde abgebrochen."
                )
            pending_migrations.append(
                (table, create_sql, copy_sql)
            )

        if pending_migrations:
            connection.execute("BEGIN IMMEDIATE")
            try:
                for table, create_sql, copy_sql in pending_migrations:
                    migration_table = f"{table}_integer_migration"
                    connection.execute(create_sql)
                    connection.execute(copy_sql)
                    connection.execute(f"DROP TABLE {table}")
                    connection.execute(
                        f"ALTER TABLE {migration_table} RENAME TO {table}"
                    )
                connection.commit()
            except sqlite3.Error:
                connection.rollback()
                raise
