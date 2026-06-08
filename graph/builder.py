# graph/builder.py
# Construye y compila el grafo de LangGraph con todos los nodos y aristas.

from langgraph.graph import StateGraph, END

from graph.state import SportAnalysisState
from agents.researcher import researcher_agent
from agents.sports_analyst import sports_analyst
from agents.critic import critic, should_continue


def build_graph() -> StateGraph:
    """
    Ensambla el grafo con los nodos y sus conexiones:

        START → researcher_agent → sports_analyst → critic
                    ↑                                  |
                    |_____ needs_revision _____________|
                                                       |
                                              approved → END
    """
    workflow = StateGraph(SportAnalysisState)

    # ── Registrar nodos ──────────────────────────────────────────────────────
    workflow.add_node("researcher_agent", researcher_agent)
    workflow.add_node("sports_analyst", sports_analyst)
    workflow.add_node("critic", critic)

    # ── Definir punto de entrada ─────────────────────────────────────────────
    workflow.set_entry_point("researcher_agent")

    # ── Aristas directas ─────────────────────────────────────────────────────
    workflow.add_edge("researcher_agent", "sports_analyst")
    workflow.add_edge("sports_analyst", "critic")

    # ── Arista condicional desde el critic ───────────────────────────────────
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "approved": END,
            "needs_revision": "researcher_agent",  # Bucle de corrección
        },
    )

    return workflow.compile()
