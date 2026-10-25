from src.domain import Assessment, AssessmentType


class ExamAssessment(Assessment):
<<<<<<< HEAD
    """Experimentelle Prüfungsart mit spezialisiertem Verhalten."""

=======
>>>>>>> c56f0385ede37abd6839a9608bb6d2bd718a4955
    def description(self) -> str:
        return "Klausur"


class PortfolioAssessment(Assessment):
<<<<<<< HEAD
    """Experimentelle Prüfungsart mit spezialisiertem Verhalten."""

=======
>>>>>>> c56f0385ede37abd6839a9608bb6d2bd718a4955
    def description(self) -> str:
        return "Portfolio"


<<<<<<< HEAD
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
=======
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
>>>>>>> c56f0385ede37abd6839a9608bb6d2bd718a4955
