from src.domain import Assessment, AssessmentType


class ExamAssessment(Assessment):
    def description(self) -> str:
        return "Klausur"


class PortfolioAssessment(Assessment):
    def description(self) -> str:
        return "Portfolio"


assessments = (
    ExamAssessment(AssessmentType.EXAM),
    PortfolioAssessment(AssessmentType.PORTFOLIO),
)

for assessment in assessments:
    print(
        assessment.description(),
        "| Prüfungsart:", assessment.assessment_type.value,
        "| Assessment-Unterklasse:", isinstance(assessment, Assessment),
    )