# 🏟️ Sports Analyst — LangGraph Pipeline

Pipeline multi-agente para análisis deportivos con tono periodístico, construido con **LangGraph**.

## Arquitectura

```
START → researcher_agent → sports_analyst → critic
             ↑                                 |
             |_____ needs_revision ____________|
                                               |
                                      approved → END
```

| Nodo               | Rol                                                              |
|--------------------|------------------------------------------------------------------|
| `researcher_agent` | Busca estadísticas y datos en la web con Tavily                  |
| `sports_analyst`   | Redacta el análisis con tono periodístico deportivo              |
| `critic`           | Valida neutralidad, precisión y calidad. Aprueba o pide revisión |

## Instalación

```bash
# 1. Crea y activa un entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Configura tus API keys
cp .env.example .env
# Edita .env con tus claves de OpenAI y Tavily
```

## Obtener las API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Tavily**: https://app.tavily.com (tiene plan gratuito)

## Uso

```bash
python main.py
```

O importa la función `run` desde tu propio script:

```python
from main import run

análisis = run("¿Cuántos goles lleva Mbappé en el Real Madrid?")
print(análisis)
```

## Estructura de archivos

```
sports-analyst/
├── main.py                  # Punto de entrada
├── requirements.txt
├── .env.example
├── graph/
│   ├── state.py             # Estado compartido (SportAnalysisState)
│   └── builder.py           # Construcción y compilación del grafo
└── agents/
    ├── researcher.py        # Nodo 1: búsqueda web con Tavily
    ├── sports_analyst.py    # Nodo 2: redacción periodística
    └── critic.py            # Nodo 3: validación + enrutamiento condicional
```

## Configuración avanzada

En `agents/critic.py` puedes ajustar:
- `MAX_ITERATIONS`: número máximo de ciclos de revisión (por defecto `3`)

En `agents/researcher.py`:
- `max_results` de Tavily (por defecto `5`)
