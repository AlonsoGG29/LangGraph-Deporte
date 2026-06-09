# agents/critic.py  (versión simplificada que usa el subgrafo)

from graph.state import SportAnalysisState
from agents.critic_subgraph import build_critic_subgraph

_critic_subgraph = build_critic_subgraph()


def critic(state: SportAnalysisState) -> SportAnalysisState:
    """Delega la evaluación al subgrafo del crítico."""
    result = _critic_subgraph.invoke({
        "question": state["question"],
        "analysis": state["analysis"],
        "iterations": state.get("iterations", 0),
    })
    return {
        "critic_decision": result["critic_decision"],
        "critic_feedback": result["critic_feedback"],
        "human_feedback": "",
    }


def human_feedback_node(state: SportAnalysisState) -> SportAnalysisState:
    pass


def should_continue(state: SportAnalysisState) -> str:
    return "human_feedback"