"""
Primer agente con herramientas y traza de decisión
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.4 - Bloque 21 [Actividad práctica]
"""
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)

# --------------------------------------------------------------------------
# 1. Definición de herramientas con docstring descriptivo y manejo de errores
# --------------------------------------------------------------------------
@tool
def consultar_estado_envio(numero_seguimiento: str) -> str:
    """Consulta el estado actual de un envío a partir de su número de seguimiento.
    Usar cuando el usuario pregunta dónde está su paquete o pedido."""
    estados = {
        "AR12345": "en tránsito, llega en 2 días",
        "AR67890": "entregado con éxito",
    }
    try:
        return estados[numero_seguimiento.strip()]
    except KeyError:
        return f"No se encontró un envío con el número {numero_seguimiento}."


@tool
def calcular_costo_envio(peso_kg: float, distancia_km: float) -> str:
    """Calcula el costo estimado de un envío según su peso en kg y la distancia en km.
    Usar cuando el usuario pregunta cuánto va a costar enviar algo."""
    try:
        costo = 500 + (float(peso_kg) * 120) + (float(distancia_km) * 3)
        return f"El costo estimado es de ${costo:.2f}."
    except Exception as e:
        return f"Error al calcular costo: {e}"


# --------------------------------------------------------------------------
# 2. Construcción del Agente
# --------------------------------------------------------------------------
def construir_agente(modelo):
    """
    Construye y devuelve un AgentExecutor con return_intermediate_steps=True
    para poder auditar la traza de decisiones del modelo.
    """
    herramientas = [consultar_estado_envio, calcular_costo_envio]

    prompt_agente = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente de logística que responde preguntas usando las "
            "herramientas disponibles cuando las necesites. Si la consulta no requiere "
            "ninguna herramienta, responde directamente con cortesía.",
        ),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

    ejecutor = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
    )
    return ejecutor


if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)
    ejecutor = construir_agente(modelo)

    print("==================================================")
    print("Prueba 1: Consulta de estado (debe invocar consultar_estado_envio)")
    print("==================================================")
    r1 = ejecutor.invoke({"entrada": "¿Dónde está mi pedido AR12345?"})
    print(f"\nRespuesta: {r1['output']}")
    herramienta_usada_1 = r1["intermediate_steps"][0][0].tool
    print(f"Traza verificada: se invocó '{herramienta_usada_1}'\n")

    print("==================================================")
    print("Prueba 2: Pregunta general (no debe usar herramientas)")
    print("==================================================")
    r2 = ejecutor.invoke({"entrada": "¿Cómo puedo contactar a soporte?"})
    print(f"\nRespuesta: {r2['output']}")
    print(f"Pasos intermedios: {r2['intermediate_steps']} (vacío, tal como se esperaba)")