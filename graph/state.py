# graph/state.py
# Define el estado compartido que viaja por todos los nodos del grafo.

from typing import TypedDict, Annotated
import operator


class SportAnalysisState(TypedDict):
    # Pregunta original del usuario
    question: str

    # Datos crudos recogidos por el researcher (URLs, estadísticas, etc.)
    raw_data: str

    # Análisis redactado por el sports_analyst
    analysis: str

    # Feedback del critic cuando rechaza el análisis
    critic_feedback: str

    # Número de iteraciones para evitar bucles infinitos
    iterations: int

    # Decisión final del critic: "approved" o "needs_revision"
    critic_decision: str

    # Feedback del usuario humano en el bucle human-in-the-loop
    human_feedback: str
