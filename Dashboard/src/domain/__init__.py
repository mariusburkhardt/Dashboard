"""Fachklassen des Dashboards."""

from .pruefungsleistung import Assessment, AssessmentStatus, AssessmentType
from .modul import Module
from .semester import Semester
from .studiengang import StudyProgram

__all__ = [
    "Assessment",
    "AssessmentStatus",
    "AssessmentType",
    "Module",
    "Semester",
    "StudyProgram",
]
