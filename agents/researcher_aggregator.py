# agents/researcher_aggregator.py
# Nodo de convergencia (fan-in): Agrega datos de múltiples fuentes paralelas

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import SportAnalysisState

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_BASE_URL"),
    model="gpt-4o-mini",
    temperature=0,
)

SYSTEM_PROMPT = """Eres un investigador que agrega datos de múltiples fuentes.
Tu trabajo es:
1. Revisar datos de Tavily, Wikipedia y otras fuentes
2. Extraer los datos más relevantes y verificables
3. Eliminar duplicados
4. Proporcionar un resumen coherente y bien estructurado

Devuelve solo datos crudos verificables, sin análisis ni opiniones."""


def researcher_aggregator(state: SportAnalysisState) -> SportAnalysisState:
    """
    Nodo de convergencia que agrega datos de múltiples fuentes paralelas.
    Combina los resultados de researcher_tavily y researcher_wikipedia.
    """
    question = state["question"]
    feedback = state.get("human_feedback", "") or state.get("critic_feedback", "")
    iterations = state.get("iterations", 0)
    
    # raw_data_sources es una lista gracias a operator.add en el State
    raw_sources = state.get("raw_data_sources", [])

    print(f"\n📊 [Aggregator] Combinando {len(raw_sources)} fuentes (iteración {iterations})...")

    # Combinar todas las fuentes
    combined_sources = "\n\n".join(raw_sources)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Pregunta: {question}

Datos de múltiples fuentes:
{combined_sources}

{'Feedback a considerar: ' + feedback if feedback else ''}

Extrae y organiza los datos más relevantes y verificables.""")
    ]

    response = llm.invoke(messages)

    print(f"✅ [Aggregator] Datos consolidados ({len(response.content)} chars)")

    return {
        "raw_data": response.content,  # Campo unificado para sports_analyst
        "iterations": iterations + 1,
    }
