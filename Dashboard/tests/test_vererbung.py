from src.domain import Assessment, AssessmentType


class ExamAssessment(Assessment):
    """Experimentelle Prüfungsart mit spezialisiertem Verhalten."""

    def description(self) -> str:
        """Liefert die Beschreibung der Prüfungsart."""
        return "Klausur"


class PortfolioAssessment(Assessment):
    """Experimentelle Prüfungsart mit spezialisiertem Verhalten."""

    def description(self) -> str:
        """Liefert die Beschreibung der Prüfungsart."""
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
