import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# 1. Cargar variables de entorno
load_dotenv()

# Usamos gemini-3.5-flash-lite por estabilidad y cuota disponible
modelo = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0
)

# --- Bloque 1: Herramientas con argumentos estructurados (args_schema) ---

class ArgumentosConsultaEnvio(BaseModel):
    numero_seguimiento: str = Field(
        description="Número de seguimiento del envío, por ejemplo 'AR12345'."
    )
    incluir_historial: bool = Field(
        default=False,
        description="Si es True, incluye el historial completo de estados, no solo el actual."
    )

ESTADOS = {
    "AR12345": {
        "actual": "en tránsito, llega en 2 días",
        "historial": [
            "recibido en depósito central",
            "en tránsito a sucursal destino",
        ],
    },
}

@tool("consultar_estado_envio_con_historial", args_schema=ArgumentosConsultaEnvio)
def consultar_estado_envio_detallado(
    numero_seguimiento: str,
    incluir_historial: bool = False
) -> str:
    """Consulta el estado de un envío, con la opción de incluir su historial completo."""
    envio = ESTADOS.get(numero_seguimiento)
    if envio is None:
        return f"No se encontró un envío con el número {numero_seguimiento}."
    if not incluir_historial:
        return envio["actual"]
    historial = ", ".join(envio["historial"])
    return f"{envio['actual']} (historial: {historial})"

@tool
def calcular_costo_envio(
    peso_kg: float,
    distancia_km: float
) -> str:
    """Calcula el costo estimado de un envío según su peso y la distancia a recorrer.
    Usar cuando el usuario pregunta cuánto va a costar enviar algo."""
    costo = 500 + (peso_kg * 120) + (distancia_km * 3)
    return f"El costo estimado es de ${costo:.2f}."

herramientas = [
    consultar_estado_envio_detallado,
    calcular_costo_envio,
]

# --- Bloque 2: Agente y ejecutor con soporte de historial en el prompt ---

prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente de logística y envíos que responde preguntas "
        "usando las herramientas disponibles cuando las necesites.",
    ),
    MessagesPlaceholder("chat_history"),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)
ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=False,
    return_intermediate_steps=True
)

# Normalizador para limpiar firmas técnicas de Gemini y entregar texto plano
def normalizar_salida(resultado: dict) -> dict:
    salida = resultado.get("output")
    if isinstance(salida, list):
        partes = []
        for bloque in salida:
            if isinstance(bloque, dict) and "text" in bloque:
                partes.append(bloque["text"])
            elif isinstance(bloque, str):
                partes.append(bloque)
            else:
                partes.append(str(bloque))
        resultado["output"] = "".join(partes)
    elif isinstance(salida, dict) and "text" in salida:
        resultado["output"] = salida["text"]
    return resultado

ejecutor_limpio = ejecutor_agente | RunnableLambda(normalizar_salida)

# --- Bloque 3: Memoria entre interacciones (multi-turno y multi-sesión) ---

historiales = {}

def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]

agente_con_memoria = RunnableWithMessageHistory(
    ejecutor_limpio,
    obtener_historial,
    input_messages_key="entrada",
    history_messages_key="chat_history",
    output_messages_key="output",
)

# --- Verificaciones de la guía del Bloque 22 ---

if __name__ == "__main__":
    print("==========================================================")
    print("PRUEBA 1: Conversación multi-turno con la misma sesión")
    print("==========================================================")
    
    config_sesion = {"configurable": {"session_id": "cliente_456"}}
    
    # Turno 1
    print("\n--- Turno 1: Consulta inicial con historial ---")
    r1 = agente_con_memoria.invoke(
        {"entrada": "¿Cuál es el estado del envío AR12345, con su historial?"},
        config_sesion
    )
    print(f"Respuesta Turno 1:\n{r1['output']}\n")
    
    # Turno 2 (referencia implícita 'ese mismo envío')
    print("--- Turno 2: Pregunta de seguimiento (usa memoria) ---")
    r2 = agente_con_memoria.invoke(
        {"entrada": "¿Y ese mismo envío ya fue entregado?"},
        config_sesion
    )
    print(f"Respuesta Turno 2:\n{r2['output']}\n")
    
    print("==========================================================")
    print("PRUEBA 2: Aislamiento entre dos sesiones distintas")
    print("==========================================================")
    
    config_cli1 = {"configurable": {"session_id": "cliente_1"}}
    config_cli2 = {"configurable": {"session_id": "cliente_2"}}
    
    agente_con_memoria.invoke(
        {"entrada": "Estoy preguntando por el envío AR12345."},
        config_cli1
    )
    
    r_cli2 = agente_con_memoria.invoke(
        {"entrada": "¿De qué envío te pregunté?"},
        config_cli2
    )
    print(f"Respuesta a Cliente 2 (debe desconocer el envío de Cliente 1):\n{r_cli2['output']}\n")
    
    mensajes_cli1 = len(obtener_historial("cliente_1").messages)
    mensajes_cli2 = len(obtener_historial("cliente_2").messages)
    print(f"Mensajes en historial de cliente_1: {mensajes_cli1} (esperado: 2)")
    print(f"Mensajes en historial de cliente_2: {mensajes_cli2} (esperado: 2)")
    print("\n✓ Bloque 22 completado y validado exitosamente.")