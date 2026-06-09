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
                    |_____ human_feedback (interruption) 
                    |         ↓
                    |    Usuario aprueba → END
                    |    Usuario rechaza ↓
                    |_____________________

    El nodo human_feedback usa breakpoint para permitir al usuario revisar
    y proporcionar feedback sobre la decisión del crítico OBLIGATORIAMENTE.
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
    workflow.add_edge("critic", "human_feedback")  # SIEMPRE va a human_feedback

    # ── Retorno desde human_feedback ─────────────────────────────────────────
    workflow.add_edge("human_feedback", END)  # Va directo a END después de feedback

    # ── Compilar con checkpointer y breakpoint ──────────────────────────────
    checkpointer = MemorySaver()
    return workflow.compile(
        interrupt_before=["human_feedback"],
        checkpointer=checkpointer
    )
