from __future__ import annotations

from datetime import date

from .dto import (
    DashboardData,
    ModuleDashboardRow,
    OverallStatus,
    TargetStatus,
)
from .domain import AssessmentStatus, StudyProgram


class DashboardService:
    """Berechnet Kennzahlen des Dashboards aus dem Fachmodell."""

    def build_dashboard_data(
        self, program: StudyProgram, today: date | None = None
    ) -> DashboardData:
        """Erstellt die aufbereiteten Dashboard-Daten für einen Studiengang."""
        current_semester = program.current_semester(today)
        elapsed_planned_semesters = min(
            current_semester - 1, program.planned_semesters
        )
        expected_ects = (
            program.required_ects
            * elapsed_planned_semesters
            / program.planned_semesters
        )
        modules = tuple(
            ModuleDashboardRow(
                semester_number=semester.number,
                module_name=module.name,
                ects=module.ects,
                assessment_type=module.assessment.assessment_type.value,
                assessment_status=module.assessment.status.value,
                grade=module.assessment.grade,
            )
            for semester in program.semesters
            for module in semester.modules
        )
        completed_ects = sum(
            module.ects
            for semester in program.semesters
            for module in semester.modules
            if module.assessment.status is AssessmentStatus.PASSED
        )
        grades = [
            module.assessment.grade
            for semester in program.semesters
            for module in semester.modules
            if module.assessment.status is AssessmentStatus.PASSED
            and module.assessment.grade is not None
        ]
        average_grade = sum(grades) / len(grades) if grades else None
        time_status = (
            TargetStatus.BEHIND
            if current_semester > program.planned_semesters
            else TargetStatus.ON_TRACK
        )
        ects_status = (
            TargetStatus.ON_TRACK
            if completed_ects >= expected_ects
            else TargetStatus.BEHIND
        )
        grade_status = (
            TargetStatus.NO_DATA
            if average_grade is None
            else TargetStatus.ON_TRACK
            if average_grade <= program.target_grade
            else TargetStatus.BEHIND
        )

        if time_status is TargetStatus.BEHIND:
            overall_status = OverallStatus.OVERDUE
        elif (
            ects_status is TargetStatus.BEHIND
            or grade_status is not TargetStatus.ON_TRACK
        ):
            overall_status = OverallStatus.AT_RISK
        else:
            overall_status = OverallStatus.ON_TRACK

        return DashboardData(
            program_name=program.name,
            student_name=program.student_name,
            current_semester=current_semester,
            planned_semesters=program.planned_semesters,
            remaining_semesters=max(
                0, program.planned_semesters - current_semester
            ),
            required_ects=program.required_ects,
            completed_ects=completed_ects,
            progress_percentage=min(
                100.0, completed_ects / program.required_ects * 100
            ),
            expected_ects=expected_ects,
            target_grade=program.target_grade,
            average_grade=average_grade,
            time_status=time_status,
            ects_status=ects_status,
            grade_status=grade_status,
            overall_status=overall_status,
            modules=modules,
        )
