# agents/sports_analyst.py
# Nodo 2: Sports Analyst
# Toma los datos crudos del researcher y redacta un análisis
# con tono periodístico deportivo.

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import SportAnalysisState

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://aggfoundry.openai.azure.com/openai/v1",
    model="gpt-4o-mini",
    temperature=0.7,
)

SYSTEM_PROMPT = """Eres un analista deportivo con estilo periodístico. Tu trabajo es:
1. Tomar datos crudos y redactar un análisis BREVE pero completo (máximo 2-3 párrafos).
2. Usar un tono como el de un artículo de marca o ESPN: directo, apasionado, pero riguroso.
3. Ser conciso: sin florituras ni descripciones extensas. Ve directo al punto.
4. Estructurar brevemente: párrafo inicial con dato clave, párrafo de contexto/análisis, cierre corto.
5. Mantener neutralidad cuando se comparan equipos o jugadores rivales.
6. NO inventar datos. Solo usa lo que te proporciona el investigador.

Recuerda: ¡Sé BREVE! El lector quiere respuestas rápidas y concisas.
Escribe en español."""


def sports_analyst(state: SportAnalysisState) -> SportAnalysisState:
    """
    Redacta el análisis deportivo a partir de los datos del researcher.
    """
    question = state["question"]
    raw_data = state["raw_data"]
    feedback = state.get("critic_feedback", "")

    print(f"\n✍️  [Sports Analyst] Redactando análisis...")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Pregunta original del usuario: {question}

Datos investigados:
{raw_data}

{'El crítico ha señalado lo siguiente para mejorar: ' + feedback if feedback else ''}

Redacta un análisis deportivo completo y atractivo.""")
    ]

    response = llm.invoke(messages)

    print(f"✅ [Sports Analyst] Análisis listo ({len(response.content)} chars)")

    return {
        **state,
        "analysis": response.content,
    }
