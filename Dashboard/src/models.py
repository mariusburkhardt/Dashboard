from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Assessment:
    name: str
    grade: Optional[float] = None
    ects: float = 0.0
    passed: bool = False
    comment: str = ""

    def is_completed(self) -> bool:
        return self.passed or self.grade is not None


@dataclass
class Module:
    code: str
    name: str
    ects: float
    assessments: List[Assessment] = field(default_factory=list)
    completed: bool = False

    def earned_ects(self) -> float:
        return self.ects if self.completed else 0.0

    def average_grade(self) -> Optional[float]:
        grades = [assessment.grade for assessment in self.assessments if assessment.grade is not None]
        if not grades:
            return None
        return sum(grades) / len(grades)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "ects": self.ects,
            "completed": self.completed,
            "assessments": [assessment.__dict__ for assessment in self.assessments],
        }

    @staticmethod
    def from_dict(data: dict) -> "Module":
        assessments = [Assessment(**assessment_data) for assessment_data in data.get("assessments", [])]
        return Module(
            code=data["code"],
            name=data["name"],
            ects=data["ects"],
            completed=data.get("completed", False),
            assessments=assessments,
        )


@dataclass
class Semester:
    number: int
    modules: List[Module] = field(default_factory=list)

    def total_ects(self) -> float:
        return sum(module.ects for module in self.modules)

    def completed_ects(self) -> float:
        return sum(module.earned_ects() for module in self.modules)

    def average_grade(self) -> Optional[float]:
        module_grades = [grade for module in self.modules if (grade := module.average_grade()) is not None]
        if not module_grades:
            return None
        return sum(module_grades) / len(module_grades)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "modules": [module.to_dict() for module in self.modules],
        }

    @staticmethod
    def from_dict(data: dict) -> "Semester":
        modules = [Module.from_dict(module_data) for module_data in data.get("modules", [])]
        return Semester(number=data["number"], modules=modules)


@dataclass
class StudyProgram:
    name: str
    target_years: int = 3
    target_grade: float = 2.0
    required_ects: float = 180.0
    semesters: List[Semester] = field(default_factory=list)

    def total_ects(self) -> float:
        return sum(semester.total_ects() for semester in self.semesters)

    def completed_ects(self) -> float:
        return sum(semester.completed_ects() for semester in self.semesters)

    def progress_percentage(self) -> float:
        if self.required_ects <= 0:
            return 0.0
        return min(100.0, (self.completed_ects() / self.required_ects) * 100.0)

    def average_grade(self) -> Optional[float]:
        semester_grades = [grade for semester in self.semesters if (grade := semester.average_grade()) is not None]
        if not semester_grades:
            return None
        return sum(semester_grades) / len(semester_grades)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "target_years": self.target_years,
            "target_grade": self.target_grade,
            "required_ects": self.required_ects,
            "semesters": [semester.to_dict() for semester in self.semesters],
        }

    @staticmethod
    def from_dict(data: dict) -> "StudyProgram":
        semesters = [Semester.from_dict(semester_data) for semester_data in data.get("semesters", [])]
        return StudyProgram(
            name=data["name"],
            target_years=data.get("target_years", 3),
            target_grade=data.get("target_grade", 2.0),
            required_ects=data.get("required_ects", 180.0),
            semesters=semesters,
        )
