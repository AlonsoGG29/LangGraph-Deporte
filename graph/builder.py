# graph/builder.py
# Construye y compila el grafo de LangGraph con paralelización.
# Patrón: START → [researcher_tavily, researcher_wikipedia] → aggregator → analyst → critic

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import SportAnalysisState
from agents.researcher_tavily import researcher_tavily
from agents.researcher_wikipedia import researcher_wikipedia
from agents.researcher_aggregator import researcher_aggregator
from agents.sports_analyst import sports_analyst
from agents.critic import critic, human_feedback_node, should_continue


def build_graph():
    """
    Grafo con paralelización (fan-out y fan-in):
    
                    ┌─→ [researcher_tavily] ─┐
    START → START ─┤                         ├→ aggregator → analyst → critic → human_feedback → END
                    └─→ [researcher_wikipedia]┘
    
    Los nodos researcher_tavily y researcher_wikipedia se ejecutan en PARALELO.
    Sus resultados se combinan en researcher_aggregator usando operator.add.
    """
    workflow = StateGraph(SportAnalysisState)

    # ── Registrar nodos ──────────────────────────────────────────────────────
    # Nodos de búsqueda paralelos (fan-out)
    workflow.add_node("researcher_tavily", researcher_tavily)
    workflow.add_node("researcher_wikipedia", researcher_wikipedia)
    
    # Nodo de convergencia (fan-in)
    workflow.add_node("researcher_aggregator", researcher_aggregator)
    
    # Resto de nodos
    workflow.add_node("sports_analyst", sports_analyst)
    workflow.add_node("critic", critic)
    workflow.add_node("human_feedback", human_feedback_node)

    # ── Definir punto de entrada ─────────────────────────────────────────────
    workflow.set_entry_point(START)

    # ── FAN-OUT: START se conecta a múltiples nodos en paralelo ──────────────
    workflow.add_edge(START, "researcher_tavily")
    workflow.add_edge(START, "researcher_wikipedia")

    # ── FAN-IN: Múltiples nodos convergen en aggregator ────────────────────
    workflow.add_edge("researcher_tavily", "researcher_aggregator")
    workflow.add_edge("researcher_wikipedia", "researcher_aggregator")

    # ── Flujo secuencial después de agregación ──────────────────────────────
    workflow.add_edge("researcher_aggregator", "sports_analyst")
    workflow.add_edge("sports_analyst", "critic")
    workflow.add_edge("critic", "human_feedback")
    workflow.add_edge("human_feedback", END)

    # ── Compilar con checkpointer y breakpoint ──────────────────────────────
    checkpointer = MemorySaver()
    return workflow.compile(
        interrupt_before=["human_feedback"],
        checkpointer=checkpointer
    )
