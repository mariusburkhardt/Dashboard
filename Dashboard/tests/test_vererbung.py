from src.domain import Assessment, AssessmentType


class ExamAssessment(Assessment):
    """Experimentelle Prüfungsart mit spezialisiertem Verhalten."""

    def description(self) -> str:
        return "Klausur"


class PortfolioAssessment(Assessment):
    """Experimentelle Prüfungsart mit spezialisiertem Verhalten."""

    def description(self) -> str:
        return "Portfolio"


def test_assessment_subclasses_inherit_and_specialize_behavior() -> None:
    """Zeigt Vererbung und Methodenüberschreibung für Prüfungsarten."""
    assessments = (
        ExamAssessment(AssessmentType.EXAM),
        PortfolioAssessment(AssessmentType.PORTFOLIO),
    )

    assert all(isinstance(assessment, Assessment) for assessment in assessments)
    assert [assessment.description() for assessment in assessments] == [
        "Klausur",
        "Portfolio",
    ]