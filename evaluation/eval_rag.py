from src.orchestrator import OrchestratorAgent
from src.rag import SimpleFAQVectorStore
from src.sub_agents import ComparisonAgent, DataAgent, RAGAgent


def run_evaluation():
    # Setup agents
    rag_store = SimpleFAQVectorStore("data/raw_faq.txt")
    data_agent = DataAgent("data/survey_responses.json")
    rag_agent = RAGAgent(rag_store)
    comp_agent = ComparisonAgent(data_agent)

    orchestrator = OrchestratorAgent(data_agent, rag_agent, comp_agent)

    eval_questions = [
        "What is our CSAT target and what happens if we fall below it?",
        "What are our peak hour wait times and how are complaints handled?",
        "How are food quality issues compensated during long delays?",
    ]

    print("=" * 80)
    print("MINISENSE RAG EVALUATION CHECKPOINT")
    print("=" * 80)

    for idx, q in enumerate(eval_questions, 1):
        print(f"\n--- Question {idx}: {q} ---")
        res = orchestrator.run(q)

        print("\n[Retrieved Chunks]:")
        for chunk in res.retrieved_context:
            print(f"  • {chunk.replace(chr(10), ' ')}")

        print("\n[Final Synthesized Answer]:")
        print(f"  {res.narrative_answer}\n")


if __name__ == "__main__":
    run_evaluation()