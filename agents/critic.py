# agents/critic.py
# Nodo 3: Critic
# Valida el análisis redactado por el sports_analyst.
# Decide si aprobarlo (→ END) o devolverlo con feedback (→ researcher_agent).
# Incluye un punto de interrupción (breakpoint) para human-in-the-loop.

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import SportAnalysisState

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://aggfoundry.openai.azure.com/openai/v1",
    model="gpt-4o-mini",
    temperature=0,
)

MAX_ITERATIONS = 3  # Máximo de ciclos antes de forzar la aprobación

SYSTEM_PROMPT = """Eres un editor crítico de contenido deportivo. Tu trabajo es evaluar análisis deportivos.

Debes revisar:
1. NEUTRALIDAD: ¿Es imparcial cuando compara equipos/jugadores?
2. PRECISIÓN: ¿Los datos de goles, títulos y estadísticas parecen coherentes y verificables?
3. EMOCIÓN Y CALIDAD: ¿Tiene gancho periodístico? ¿Es atractivo de leer?
4. COMPLETITUD: ¿Responde realmente a la pregunta original?

Responde ÚNICAMENTE con un JSON válido en este formato exacto:
{
  "decision": "approved" | "needs_revision",
  "feedback": "string con correcciones específicas (vacío si approved)",
  "score": número del 1 al 10
}"""


def critic(state: SportAnalysisState) -> SportAnalysisState:
    """
    Evalúa el análisis. Devuelve 'approved' o 'needs_revision' con feedback.
    """
    question = state["question"]
    analysis = state["analysis"]
    iterations = state.get("iterations", 0)
    human_feedback = state.get("human_feedback", "")

    print(f"\n🔎 [Critic] Evaluando análisis (iteración {iterations})...")

    # Si ya alcanzamos el máximo de iteraciones, aprobamos para evitar bucle infinito
    if iterations >= MAX_ITERATIONS:
        print(f"⚠️  [Critic] Máximo de iteraciones alcanzado. Aprobando forzosamente.")
        return {
            "critic_decision": "approved",
            "critic_feedback": "",
            "human_feedback": "",
        }

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Pregunta original: {question}

Análisis a evaluar:
{analysis}

Evalúa el análisis y devuelve el JSON.""")
    ]

    response = llm.invoke(messages)

    # Parseamos el JSON de respuesta
    try:
        # Limpiamos posibles bloques de markdown
        raw = response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw)
        decision = result.get("decision", "approved")
        feedback = result.get("feedback", "")
        score = result.get("score", 0)
    except (json.JSONDecodeError, KeyError):
        # Si falla el parseo, aprobamos por defecto
        print("⚠️  [Critic] Error al parsear respuesta. Aprobando por defecto.")
        decision = "approved"
        feedback = ""
        score = "N/A"

    status = "✅ APROBADO" if decision == "approved" else "❌ NECESITA REVISIÓN"
    print(f"{status} | Score: {score}/10")
    if feedback:
        print(f"📝 Feedback: {feedback[:120]}...")

    return {
        "critic_decision": decision,
        "critic_feedback": feedback,
        "human_feedback": "",  # Reset human_feedback para próxima iteración
    }


def human_feedback_node(state: SportAnalysisState) -> SportAnalysisState:
    """
    Nodo de no-op para human-in-the-loop.
    Se interrumpe aquí para permitir al usuario revisar y dar feedback.
    """
    pass


def should_continue(state: SportAnalysisState) -> str:
    """
    Función de enrutamiento condicional:
    Siempre envía a human_feedback para que el usuario apruebe o rechace.
    """
    return "human_feedback"
