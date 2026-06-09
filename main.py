# main.py
# Punto de entrada principal. Carga variables de entorno y ejecuta el grafo.
# Implementa human-in-the-loop OBLIGATORIO con breakpoints y update_state.

from dotenv import load_dotenv
load_dotenv()

from graph.builder import build_graph


def run(question: str) -> str:
    """
    Ejecuta el pipeline completo con paralelización y human-in-the-loop OBLIGATORIO.
    Los investigadores (Tavily y Wikipedia) se ejecutan en PARALELO.
    El usuario DEBE aprobar o rechazar el análisis antes de finalizar.
    """
    graph = build_graph()

    initial_state = {
        "question": question,
        "raw_data_sources": [],  # Lista para acumular datos (operator.add)
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

    # Loop principal
    while True:
        # Ejecutar hasta el breakpoint (human_feedback)
        for event in graph.stream(initial_state if not hasattr(graph, '_state') else None, thread, stream_mode="values"):
            pass

        # Obtener estado actual (estamos interrumpidos en human_feedback)
        state_snapshot = graph.get_state(thread)
        current_state = state_snapshot.values

        # Mostrar análisis y decisión del crítico
        print("\n" + "=" * 60)
        print("📰 ANÁLISIS GENERADO")
        print("=" * 60)
        print(current_state.get("analysis", ""))
        print("\n" + "=" * 60)
        print("🔎 EVALUACIÓN DEL CRÍTICO")
        print("=" * 60)
        decision = current_state.get("critic_decision", "")
        feedback = current_state.get("critic_feedback", "")
        print(f"Decisión: {decision.upper()}")
        if feedback:
            print(f"Feedback: {feedback}")
        print("=" * 60)

        # Pedir aprobación/rechazo del usuario
        print("\n👤 FEEDBACK HUMANO - Opciones:")
        print("  1) Aprobar análisis → Finalizar")
        print("  2) Rechazar y proporcionar feedback → Mejorar")
        
        while True:
            choice = input("\n¿Qué deseas hacer? (1/2): ").strip()
            if choice in ["1", "2"]:
                break
            print("⚠️  Opción inválida. Ingresa 1 o 2.")

        if choice == "1":
            # Usuario aprueba → FIN
            print("\n✅ Análisis aprobado. Finalizando...")
            graph.update_state(thread, {"human_feedback": "APROBADO"}, as_node="human_feedback")
            for event in graph.stream(None, thread, stream_mode="values"):
                pass
            break
        else:
            # Usuario rechaza y proporciona feedback
            user_feedback = input("\n📝 Ingresa tu feedback para mejorar el análisis: ").strip()
            if not user_feedback:
                print("⚠️  Feedback vacío. Intenta de nuevo.")
                continue
            
            # Actualizar estado con feedback
            graph.update_state(thread, {"human_feedback": user_feedback}, as_node="human_feedback")
            
            # Continuar ejecución desde los investigadores paralelos
            for event in graph.stream(None, thread, stream_mode="values"):
                pass

    # Obtener estado final
    final_state = graph.get_state(thread).values

    print("\n" + "=" * 60)
    print("📰 ANÁLISIS FINAL APROBADO")
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
