import json
from typing import Any, Dict, List
from src.schemas import (
    ComparisonAgentOutput,
    DataAgentOutput,
    RAGAgentOutput,
    RAGChunk,
)
from src.tools import compute_survey_metrics


class DataAgent:

    def __init__(self, raw_json_path: str):
        with open(raw_json_path, "r") as f:
            self.dataset = json.load(f).get("responses", [])

    def execute(self, params: Dict[str, Any]) -> DataAgentOutput:
        # Calls internal deterministic metric computation tool
        metrics = compute_survey_metrics(
            self.dataset,
            business_id=params.get("business_id"),
            start_date=params.get("start_date"),
            end_date=params.get("end_date"),
        )
        return DataAgentOutput(
            total_responses=metrics["count"],
            average_rating=metrics["avg_rating"],
            csat_percentage=metrics["csat"],
            rating_distribution=metrics["distribution"],
            top_themes=metrics["themes"],
            filters_applied=params,
        )


class RAGAgent:

    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline

    def execute(self, params: Dict[str, Any]) -> RAGAgentOutput:
        query = params.get("query", "")
        top_k = params.get("top_k", 3)
        results = self.rag.retrieve(query, top_k=top_k)

        chunks = [
            RAGChunk(
                content=res["text"],
                source_query=query,
                relevance_score=res["score"],
            )
            for res in results
        ]
        context = "\n".join([c.content for c in chunks])
        return RAGAgentOutput(retrieved_chunks=chunks, summary_context=context)


class ComparisonAgent:

    def __init__(self, data_agent: DataAgent):
        self.data_agent = data_agent

    def execute(self, params: Dict[str, Any]) -> ComparisonAgentOutput:
        p1_params = params.get("period_1", {})
        p2_params = params.get("period_2", {})

        m1 = self.data_agent.execute(p1_params)
        m2 = self.data_agent.execute(p2_params)

        rating_delta = round(m2.average_rating - m1.average_rating, 2)
        csat_delta = round(m2.csat_percentage - m1.csat_percentage, 2)

        takeaways = []
        if rating_delta < 0:
            takeaways.append(
                f"Average rating declined by {abs(rating_delta)} points."
            )
        else:
            takeaways.append(f"Average rating improved by {rating_delta} points.")

        if csat_delta < 0:
            takeaways.append(f"CSAT score dropped by {abs(csat_delta)}%.")
        else:
            takeaways.append(f"CSAT score grew by {csat_delta}%.")

        return ComparisonAgentOutput(
            period_1_metrics=m1.model_dump(),
            period_2_metrics=m2.model_dump(),
            rating_delta=rating_delta,
            csat_delta=csat_delta,
            key_takeaways=takeaways,
        )