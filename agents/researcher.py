# agents/researcher.py
# Nodo 1: Researcher Agent
# Recibe la pregunta del usuario (y opcionalmente feedback del critic)
# y busca estadísticas/datos deportivos en la web con Tavily.

import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import SportAnalysisState

# Inicializamos el LLM y la herramienta de búsqueda
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://aggfoundry.openai.azure.com/openai/v1",
    model="gpt-4o-mini",
    temperature=0,
)
search_tool = TavilySearchResults(max_results=5)

SYSTEM_PROMPT = """Eres un investigador deportivo especializado. Tu trabajo es:
1. Analizar la pregunta deportiva recibida.
2. Buscar estadísticas, resultados, goles, títulos y datos relevantes y actualizados.
3. Devolver ÚNICAMENTE datos crudos y verificables (números, fechas, fuentes).

Si recibes feedback del crítico, enfócate en corregir exactamente lo que se indica.
No redactes análisis ni opiniones, solo datos."""


def researcher_agent(state: SportAnalysisState) -> SportAnalysisState:
    """
    Busca datos deportivos relevantes para la pregunta del usuario.
    Si hay feedback del critic, lo usa para refinar la búsqueda.
    """
    question = state["question"]
    feedback = state.get("critic_feedback", "")
    iterations = state.get("iterations", 0)

    # Construimos la query de búsqueda
    if feedback:
        search_query = f"{question}. Contexto adicional necesario: {feedback}"
    else:
        search_query = question

    print(f"\n🔍 [Researcher] Iteración {iterations + 1} | Buscando: {search_query[:80]}...")

    # Ejecutamos la búsqueda con Tavily
    search_results = search_tool.invoke(search_query)

    # Formateamos los resultados
    if isinstance(search_results, str):
        formatted_results = search_results
    else:
        formatted_results = "\n\n".join([
            f"Fuente: {r.get('url', 'N/A')}\n{r.get('content', '')}"
            for r in search_results if isinstance(r, dict)
        ])

    # El LLM extrae y organiza los datos más relevantes
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Pregunta: {question}

Resultados de búsqueda:
{formatted_results}

{'Feedback del crítico a tener en cuenta: ' + feedback if feedback else ''}

Resume los datos más relevantes y verificables para responder la pregunta.""")
    ]

    response = llm.invoke(messages)

    print(f"✅ [Researcher] Datos recopilados ({len(response.content)} chars)")

    return {
        **state,
        "raw_data": response.content,
        "iterations": iterations + 1,
    }
