"""Fachklassen des Studien-Dashboards."""

from .assessment import Assessment, AssessmentStatus, AssessmentType
from .module import Module
from .semester import Semester
from .study_program import StudyProgram

__all__ = [
    "Assessment",
    "AssessmentStatus",
    "AssessmentType",
    "Module",
    "Semester",
    "StudyProgram",
]
