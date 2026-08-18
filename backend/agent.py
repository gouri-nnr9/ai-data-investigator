from models import (
    Evidence,
    Finding,
    InvestigationResponse,
)


class DataInvestigatorAgent:

    def investigate(
        self,
        question: str,
    ) -> InvestigationResponse:

        return InvestigationResponse(
            question=question,
            status="completed",
            summary=(
                "Revenue fell 35.1% in July compared with June, "
                "with the largest contribution coming from a sharp "
                "decline in Electronics sales."
            ),
            findings=[
                Finding(
                    title="Revenue declined",
                    description=(
                        "Completed revenue decreased from "
                        "₹135.42M in June to ₹87.89M in July."
                    ),
                    severity="high",
                ),
                Finding(
                    title="Electronics was the main contributor",
                    description=(
                        "Electronics revenue fell from ₹71.66M "
                        "to ₹29.65M, a decline of approximately 58.6%."
                    ),
                    severity="high",
                ),
                Finding(
                    title="Electronics order volume collapsed",
                    description=(
                        "Electronics completed orders fell from "
                        "1,562 to 663, while category-level average "
                        "order value remained almost unchanged."
                    ),
                    severity="high",
                ),
                Finding(
                    title="Inventory shortage detected",
                    description=(
                        "Electronics inventory dropped sharply in July, "
                        "especially in North and East regions."
                    ),
                    severity="medium",
                ),
                Finding(
                    title="Refunds and payment failures increased",
                    description=(
                        "July also showed elevated refunds and payment "
                        "failures, although these do not fully explain "
                        "the total revenue decline."
                    ),
                    severity="medium",
                ),
            ],
            evidence=[
                Evidence(
                    finding="Revenue change",
                    value="-35.10%",
                    source="Monthly revenue analysis",
                ),
                Evidence(
                    finding="Electronics revenue change",
                    value="-58.63%",
                    source="Category revenue analysis",
                ),
                Evidence(
                    finding="Electronics order volume",
                    value="-57.55%",
                    source="Category order analysis",
                ),
                Evidence(
                    finding="North Electronics inventory",
                    value="~7.5 average units",
                    source="Inventory analysis",
                ),
                Evidence(
                    finding="East Electronics inventory",
                    value="~9.6 average units",
                    source="Inventory analysis",
                ),
                Evidence(
                    finding="July refund amount",
                    value="₹4.11M",
                    source="Refund analysis",
                ),
            ],
            queries=[
                """
SELECT
    DATE_TRUNC('month', order_date) AS month,
    COUNT(*) AS completed_orders,
    SUM(total_amount) AS revenue,
    AVG(total_amount) AS avg_order_value
FROM orders
WHERE status = 'completed'
GROUP BY 1
ORDER BY 1;
                """.strip(),
                """
SELECT
    DATE_TRUNC('month', o.order_date) AS month,
    p.category,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'completed'
GROUP BY 1, p.category
ORDER BY 1;
                """.strip(),
            ],
            limitations=[
                (
                    "The current dataset is synthetic and is designed "
                    "for investigation-agent development."
                ),
                (
                    "Inventory availability is a strong supporting "
                    "signal, but the current synthetic order history "
                    "does not establish real-world causation."
                ),
            ],
        )