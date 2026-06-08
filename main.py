# main.py
# Punto de entrada principal. Carga variables de entorno y ejecuta el grafo.

from dotenv import load_dotenv
load_dotenv()

from graph.builder import build_graph


def run(question: str) -> str:
    """
    Ejecuta el pipeline completo dado una pregunta deportiva.
    Devuelve el análisis final aprobado por el critic.
    """
    graph = build_graph()

    initial_state = {
        "question": question,
        "raw_data": "",
        "analysis": "",
        "critic_feedback": "",
        "iterations": 0,
        "critic_decision": "",
    }

    print("=" * 60)
    print(f"📣 Pregunta: {question}")
    print("=" * 60)

    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("📰 ANÁLISIS FINAL")
    print("=" * 60)
    print(final_state["analysis"])
    print("=" * 60)

    return final_state["analysis"]


if __name__ == "__main__":
    # Pedir pregunta al usuario
    pregunta = input("📝 Ingresa tu pregunta deportiva: ").strip()
    if not pregunta:
        pregunta = "¿Quién tiene más Balones de Oro, Messi o Cristiano Ronaldo, y cuántos lleva cada uno?"
        print(f"Usando pregunta por defecto: {pregunta}")
    run(pregunta)
