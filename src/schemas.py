from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Orchestrator Task Breakdown Spec
class SubTaskSpec(BaseModel):
    task_id: str
    target_agent: str  # "DataAgent", "RAGAgent", "ComparisonAgent"
    parameters: Dict[str, Any]
    description: str


class ExecutionPlan(BaseModel):
    original_query: str
    subtasks: List[SubTaskSpec]


# Sub-Agent Outputs
class DataAgentOutput(BaseModel):
    total_responses: int
    average_rating: float
    csat_percentage: float  # % of ratings >= 4
    rating_distribution: Dict[int, int]
    top_themes: List[Dict[str, Any]]
    filters_applied: Dict[str, Any]


class RAGChunk(BaseModel):
    content: str
    source_query: str
    relevance_score: float


class RAGAgentOutput(BaseModel):
    retrieved_chunks: List[RAGChunk]
    summary_context: str


class ComparisonAgentOutput(BaseModel):
    period_1_metrics: Dict[str, Any]
    period_2_metrics: Dict[str, Any]
    rating_delta: float
    csat_delta: float
    key_takeaways: List[str]


class FinalResponse(BaseModel):
    query: str
    narrative_answer: str
    data_summary: Optional[Dict[str, Any]] = None
    retrieved_context: Optional[List[str]] = None