# agents/researcher_wikipedia.py
# Nodo paralelo 2: Busca datos en Wikipedia

import os
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from graph.state import SportAnalysisState


def researcher_wikipedia(state: SportAnalysisState) -> SportAnalysisState:
    """
    Busca datos deportivos usando Wikipedia (paralelo).
    """
    question = state["question"]
    
    print(f"\n📚 [Wikipedia Researcher] Buscando: {question[:60]}...")

    try:
        wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        result = wikipedia.run(question)
        
        # Limitar resultado
        result_short = result[:500] if len(result) > 500 else result
        print(f"✅ [Wikipedia] Información encontrada")
        
        return {
            "raw_data_sources": [f"[WIKIPEDIA]\n{result_short}..."],
        }
    except Exception as e:
        print(f"⚠️  [Wikipedia] Error: {str(e)[:50]}")
        return {
            "raw_data_sources": [],
        }
