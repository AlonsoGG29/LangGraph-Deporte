# graph/builder.py
# Construye y compila el grafo de LangGraph con todos los nodos y aristas.
# Incluye human-in-the-loop en el nodo critic.

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import SportAnalysisState
from agents.researcher import researcher_agent
from agents.sports_analyst import sports_analyst
from agents.critic import critic, human_feedback_node, should_continue


def build_graph():
    """
    Ensambla el grafo con los nodos y sus conexiones:

        START → researcher_agent → sports_analyst → critic
                    ↑                                  |
                    |_____ needs_revision ← human_feedback (interruption)
                                                      |
                                            approved → END
    
    El nodo human_feedback usa breakpoint para permitir al usuario revisar
    y proporcionar feedback sobre la decisión del crítico.
    """
    workflow = StateGraph(SportAnalysisState)

    # ── Registrar nodos ──────────────────────────────────────────────────────
    workflow.add_node("researcher_agent", researcher_agent)
    workflow.add_node("sports_analyst", sports_analyst)
    workflow.add_node("critic", critic)
    workflow.add_node("human_feedback", human_feedback_node)

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
            "needs_revision": "human_feedback",  # Interrumpe para feedback humano
        },
    )

    # ── Arista desde human_feedback hacia researcher ──────────────────────────
    workflow.add_edge("human_feedback", "researcher_agent")

    # ── Compilar con checkpointer y breakpoint ──────────────────────────────
    checkpointer = MemorySaver()
    return workflow.compile(
        interrupt_before=["human_feedback"],
        checkpointer=checkpointer
    )
