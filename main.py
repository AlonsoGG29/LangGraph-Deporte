# main.py
# Punto de entrada principal. Carga variables de entorno y ejecuta el grafo.
# Implementa human-in-the-loop con breakpoints y update_state.

from dotenv import load_dotenv
load_dotenv()

from graph.builder import build_graph


def run(question: str) -> str:
    """
    Ejecuta el pipeline completo dado una pregunta deportiva.
    Incluye human-in-the-loop en el nodo critic cuando se necesita revisión.
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
        "human_feedback": "",
    }

    print("=" * 60)
    print(f"📣 Pregunta: {question}")
    print("=" * 60)

    # Thread para mantener estado en checkpointer
    thread = {"configurable": {"thread_id": "main"}}

    # Ejecutar hasta el primer breakpoint
    for event in graph.stream(initial_state, thread, stream_mode="values"):
        pass

    # Loop de human-in-the-loop
    while True:
        # Verificar si estamos interrumpidos
        try:
            # Obtener estado actual
            state = graph.get_state(thread)
            
            if state.values.get("critic_decision") == "approved":
                # Si ya fue aprobado, salimos del loop
                final_state = state.values
                break
            
            # El crítico necesita revisión, mostrar feedback
            print("\n" + "=" * 60)
            print("🔎 [Crítico] Análisis necesita revisión")
            print("=" * 60)
            print(f"Score: {state.values.get('critic_feedback', 'N/A')}")
            print(f"\n📰 Análisis actual:")
            print(state.values.get("analysis", ""))
            print("\n" + "=" * 60)
            
            # Obtener feedback del usuario
            user_feedback = input("\n👤 Ingresa tu feedback para mejorar el análisis (o presiona Enter para auto-mejorar): ").strip()
            
            # Actualizar estado con feedback del usuario
            graph.update_state(thread, {"human_feedback": user_feedback}, as_node="human_feedback")
            
            # Continuar ejecución
            for event in graph.stream(None, thread, stream_mode="values"):
                pass
                
        except Exception as e:
            print(f"⚠️  Error en loop: {e}")
            break

    # Estado final
    final_state = graph.get_state(thread).values if hasattr(graph.get_state(thread), 'values') else final_state

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
