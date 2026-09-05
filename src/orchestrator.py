import json
from typing import Any, Dict
from src.schemas import ExecutionPlan, FinalResponse, SubTaskSpec


class OrchestratorAgent:

    def __init__(self, data_agent, rag_agent, comparison_agent):
        self.data_agent = data_agent
        self.rag_agent = rag_agent
        self.comparison_agent = comparison_agent

    def plan(self, user_query: str) -> ExecutionPlan:
        # Rule-based task spec planner for deterministic execution
        subtasks = []
        q_lower = user_query.lower()

        if "compare" in q_lower or "month" in q_lower or "versus" in q_lower:
            subtasks.append(
                SubTaskSpec(
                    task_id="t1",
                    target_agent="ComparisonAgent",
                    parameters={
                        "period_1": {
                            "start_date": "2026-04-01",
                            "end_date": "2026-04-30",
                        },
                        "period_2": {
                            "start_date": "2026-05-01",
                            "end_date": "2026-05-31",
                        },
                    },
                    description="Compare April vs May 2026 metrics",
                )
            )
        else:
            subtasks.append(
                SubTaskSpec(
                    task_id="t1",
                    target_agent="DataAgent",
                    parameters={"start_date": "2026-05-01"},
                    description="Compute current period metrics",
                )
            )

        subtasks.append(
            SubTaskSpec(
                task_id="t2",
                target_agent="RAGAgent",
                parameters={"query": user_query, "top_k": 3},
                description="Retrieve operational FAQ context",
            )
        )

        return ExecutionPlan(original_query=user_query, subtasks=subtasks)

    def run(self, user_query: str) -> FinalResponse:
        plan = self.plan(user_query)
        agent_outputs = {}

        for task in plan.subtasks:
            if task.target_agent == "DataAgent":
                agent_outputs[task.task_id] = self.data_agent.execute(
                    task.parameters
                )
            elif task.target_agent == "RAGAgent":
                agent_outputs[task.task_id] = self.rag_agent.execute(
                    task.parameters
                )
            elif task.target_agent == "ComparisonAgent":
                agent_outputs[task.task_id] = self.comparison_agent.execute(
                    task.parameters
                )

        # Synthesize summary narrative
        narrative = self.synthesize(user_query, agent_outputs)

        retrieved_texts = []
        if "t2" in agent_outputs:
            retrieved_texts = [
                c.content for c in agent_outputs["t2"].retrieved_chunks
            ]

        return FinalResponse(
            query=user_query,
            narrative_answer=narrative,
            data_summary={
                k: v.model_dump()
                for k, v in agent_outputs.items()
                if k != "t2"
            },
            retrieved_context=retrieved_texts,
        )

    def synthesize(self, query: str, results: Dict[str, Any]) -> str:
        """
        Synthesizes structured sub-agent outputs and retrieved FAQ context
        into a coherent, executive-ready business narrative.
        """
        # 1. Safely extract RAG context
        rag_output = results.get("t2")
        rag_insight = ""
        if rag_output and hasattr(rag_output, "retrieved_chunks") and rag_output.retrieved_chunks:
            # Use top-1 relevant chunk and format 'A:' answer as natural prose
            top_chunk = rag_output.retrieved_chunks[0].content
            if "A:" in top_chunk:
                answer_text = top_chunk.split("A:")[1].strip()
                rag_insight = f" Operational Policy Note: {answer_text}"
            else:
                rag_insight = f" Operational Policy Note: {top_chunk.strip()}"

        # 2. Synthesize narrative based on primary task output
        primary_task = results.get("t1")
        if not primary_task:
            return f"Analysis complete for query: '{query}'."

        # Scenario A: Comparison Task (April vs May, etc.)
        if hasattr(primary_task, "csat_delta"):
            c = primary_task
            delta_str = f"+{c.csat_delta}%" if c.csat_delta > 0 else f"{c.csat_delta}%"
            rating_str = f"+{c.rating_delta}" if c.rating_delta > 0 else f"{c.rating_delta}"
            
            takeaways = " ".join(c.key_takeaways) if c.key_takeaways else ""
            
            return (
                f"Comparing the two requested periods, CSAT shifted by {delta_str} "
                f"and average satisfaction ratings moved by {rating_str} points. "
                f"{takeaways}{rag_insight}"
            ).strip()

        # Scenario B: Single-Period Data Aggregation
        if hasattr(primary_task, "csat_percentage"):
            d = primary_task
            return (
                f"Across {d.total_responses:,} customer survey responses evaluated for this period, "
                f"the business achieved an average satisfaction rating of {d.average_rating}/5.0 "
                f"with an overall CSAT score of {d.csat_percentage}%.{rag_insight}"
            ).strip()

        return f"Processed query '{query}' successfully."