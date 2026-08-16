from models import InvestigationResponse


class DataInvestigatorAgent:

    def investigate(self, question: str) -> InvestigationResponse:
        return InvestigationResponse(
            question=question,
            status="not_implemented",
            summary="The AI investigation engine is not connected yet.",
        )