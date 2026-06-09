# agents/researcher_tavily.py
# Nodo paralelo 1: Busca datos de Tavily

import os
from langchain_community.tools.tavily_search import TavilySearchResults

from graph.state import SportAnalysisState


def researcher_tavily(state: SportAnalysisState) -> SportAnalysisState:
    """
    Busca datos deportivos usando Tavily (paralelo).
    """
    question = state["question"]
    search_tool = TavilySearchResults(max_results=3)

    print(f"\n🔍 [Tavily Researcher] Buscando: {question[:60]}...")

    search_results = search_tool.invoke(question)

    if isinstance(search_results, str):
        formatted_results = search_results
    else:
        formatted_results = "\n".join([
            f"• {r.get('content', '')[:150]}"
            for r in search_results if isinstance(r, dict)
        ])

    print(f"✅ [Tavily] Encontrados {len(search_results)} resultados")

    return {
        "raw_data_sources": [f"[TAVILY]\n{formatted_results}"],
    }
