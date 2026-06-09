# graph/builder.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import SportAnalysisState
from agents.researcher_tavily import researcher_tavily
from agents.researcher_wikipedia import researcher_wikipedia
from agents.researcher_aggregator import researcher_aggregator
from agents.sports_analyst import sports_analyst
from agents.critic import critic, human_feedback_node, should_continue


def build_graph():
    workflow = StateGraph(SportAnalysisState)

    # Registrar nodos
    workflow.add_node("researcher_tavily", researcher_tavily)
    workflow.add_node("researcher_wikipedia", researcher_wikipedia)
    workflow.add_node("researcher_aggregator", researcher_aggregator)
    workflow.add_node("sports_analyst", sports_analyst)
    workflow.add_node("critic", critic)
    workflow.add_node("human_feedback", human_feedback_node)

    # FAN-OUT: START → dos researchers en paralelo
    workflow.add_edge(START, "researcher_tavily")
    workflow.add_edge(START, "researcher_wikipedia")

    # FAN-IN: ambos researchers → aggregator
    workflow.add_edge("researcher_tavily", "researcher_aggregator")
    workflow.add_edge("researcher_wikipedia", "researcher_aggregator")

    # Flujo secuencial
    workflow.add_edge("researcher_aggregator", "sports_analyst")
    workflow.add_edge("sports_analyst", "critic")
    workflow.add_edge("critic", "human_feedback")
    workflow.add_edge("human_feedback", END)

    # Compilar con checkpointer y breakpoint
    checkpointer = MemorySaver()
    return workflow.compile(
        interrupt_before=["human_feedback"],
        checkpointer=checkpointer
    )