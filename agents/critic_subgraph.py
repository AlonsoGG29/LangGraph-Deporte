# agents/critic_subgraph.py
# Sub-grafo del crítico con estado propio.
# Patrón: evaluate → generate_feedback → END

import os
import json
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_BASE_URL"),
    model="gpt-4o-mini",
    temperature=0,
)

MAX_ITERATIONS = 3


# ── Estado INTERNO del subgrafo ──────────────────────────────────────────────
class CriticState(TypedDict):
    question: str
    analysis: str
    iterations: int
    score: int           # solo existe dentro del subgrafo
    critic_decision: str
    critic_feedback: str


# ── Nodo 1: evaluar con puntuación ──────────────────────────────────────────
def evaluate(state: CriticState) -> CriticState:
    """Puntúa el análisis del 1 al 10 y decide si aprobar o revisar."""
    if state.get("iterations", 0) >= MAX_ITERATIONS:
        print("⚠️  [Critic] Máximo de iteraciones. Aprobando forzosamente.")
        return {"score": 10, "critic_decision": "approved", "critic_feedback": ""}

    response = llm.invoke([
        SystemMessage(content="""Eres un editor crítico deportivo. Evalúa el análisis.
Responde SOLO con JSON: {"decision": "approved"|"needs_revision", "score": 1-10}"""),
        HumanMessage(content=f"Pregunta: {state['question']}\n\nAnálisis:\n{state['analysis']}")
    ])

    try:
        raw = response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw)
        decision = result.get("decision", "approved")
        score = result.get("score", 7)
    except Exception:
        decision, score = "approved", 7

    print(f"🔎 [Critic/evaluate] Score: {score}/10 | Decisión: {decision.upper()}")
    return {"score": score, "critic_decision": decision}


# ── Nodo 2: generar feedback detallado (solo si needs_revision) ─────────────
def generate_feedback(state: CriticState) -> CriticState:
    """Si la decisión es needs_revision, genera feedback concreto."""
    if state.get("critic_decision") == "approved":
        return {"critic_feedback": ""}

    response = llm.invoke([
        SystemMessage(content="Eres un editor crítico. Lista las correcciones específicas necesarias en 2-3 puntos concisos."),
        HumanMessage(content=f"Pregunta: {state['question']}\n\nAnálisis:\n{state['analysis']}\n\nScore: {state.get('score')}/10")
    ])

    feedback = response.content.strip()
    print(f"📝 [Critic/feedback] {feedback[:100]}...")
    return {"critic_feedback": feedback}


# ── Compilar el subgrafo ─────────────────────────────────────────────────────
def build_critic_subgraph():
    builder = StateGraph(CriticState)
    builder.add_node("evaluate", evaluate)
    builder.add_node("generate_feedback", generate_feedback)
    builder.add_edge(START, "evaluate")
    builder.add_edge("evaluate", "generate_feedback")
    builder.add_edge("generate_feedback", END)
    return builder.compile()