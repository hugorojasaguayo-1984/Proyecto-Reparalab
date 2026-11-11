import os
import sys
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# 1. Cargar entorno y modelo
load_dotenv()

modelo = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0
)

# 2. Registro de auditoría de aprobaciones
registro_aprobaciones = []

def registrar_aprobacion(
    herramienta: str,
    argumentos: dict,
    aprobado: bool,
) -> None:
    """Registra en memoria la decisión humana tomada para auditoría."""
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "momento": datetime.now(timezone.utc).isoformat(),
    })

def esperar_aprobacion(
    mensaje: str,
    tiempo_limite_segundos: int = 300
) -> bool:
    """Solicita confirmación humana por consola. Compatible con Windows y Unix."""
    print(f"\n[SUPERVISIÓN HUMANA REQUERIDA] {mensaje}")
    try:
        respuesta = input("¿Aprobar acción? (s/n): ")
        return respuesta.strip().lower() == "s"
    except (EOFError, KeyboardInterrupt):
        return False

# --- Catálogo de Herramientas clasificadas por riesgo ---

# A) RIESGO BAJO (Solo lectura)
class ArgumentosConsultaEnvio(BaseModel):
    numero_seguimiento: str = Field(description="Número de seguimiento del envío.")
    incluir_historial: bool = Field(default=False, description="Si es True, incluye historial.")

ESTADOS = {
    "AR12345": {
        "actual": "en tránsito, llega en 2 días",
        "historial": ["recibido en depósito central", "en tránsito"],
    },
}

@tool("consultar_estado_envio_con_historial", args_schema=ArgumentosConsultaEnvio)
def consultar_estado_envio_detallado(
    numero_seguimiento: str,
    incluir_historial: bool = False
) -> str:
    """Consulta el estado de un envío. Riesgo bajo: solo lectura."""
    envio = ESTADOS.get(numero_seguimiento)
    if envio is None:
        return f"No se encontró un envío con el número {numero_seguimiento}."
    if not incluir_historial:
        return envio["actual"]
    historial = ", ".join(envio["historial"])
    return f"{envio['actual']} (historial: {historial})"

# B) RIESGO BAJO (Solo cálculo)
@tool
def calcular_costo_envio(peso_kg: float, distancia_km: float) -> str:
    """Calcula el costo estimado de un envío. Riesgo bajo: solo cálculo matemático."""
    costo = 500 + (peso_kg * 120) + (distancia_km * 3)
    return f"El costo estimado es de ${costo:.2f}."

# C) RIESGO ALTO (Impacto económico irreversible -> Requiere supervisión humana)
class ArgumentosReembolso(BaseModel):
    numero_pedido: str = Field(description="Identificador único del pedido a reembolsar.")
    monto: float = Field(description="Monto monetario exacto del reembolso.")

@tool("generar_reembolso", args_schema=ArgumentosReembolso)
def generar_reembolso(numero_pedido: str, monto: float) -> str:
    """Genera un reembolso económico. Riesgo alto: acción financiera irreversible.
    Requiere aprobación explícita de un supervisor humano antes de ejecutarse."""
    mensaje = f"El agente solicita emitir un REEMBOLSO de ${monto:.2f} para el pedido '{numero_pedido}'."
    aprobado = esperar_aprobacion(mensaje)
    
    registrar_aprobacion(
        herramienta="generar_reembolso",
        argumentos={"numero_pedido": numero_pedido, "monto": monto},
        aprobado=aprobado,
    )
    
    if not aprobado:
        return f"Reembolso de ${monto:.2f} para {numero_pedido} RECHAZADO por el supervisor humano."
    
    return f"Reembolso de ${monto:.2f} APROBADO y procesado con éxito para el pedido {numero_pedido}."

herramientas = [
    consultar_estado_envio_detallado,
    calcular_costo_envio,
    generar_reembolso,
]

# --- Agente con retorno de intermediate_steps para trazas ---

prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un agente de operaciones y logística. Usa las herramientas "
        "apropiadas según la solicitud. Si se te pide un reembolso, usa generar_reembolso.",
    ),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)
ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True,
    return_intermediate_steps=True
)

# --- Persistencia de Trazas de Decisión y Detección de Anomalías ---

def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
    archivo: str = "trazas_agente.jsonl"
) -> None:
    """Guarda una interacción completa en archivo JSONL para auditoría posterior."""
    salida = resultado.get("output", "")
    if isinstance(salida, list):
        salida_str = "".join(
            b.get("text", "") if isinstance(b, dict) else str(b)
            for b in salida
        )
    elif isinstance(salida, dict):
        salida_str = salida.get("text", str(salida))
    else:
        salida_str = str(salida)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": salida_str
    }
    
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

def marcar_repeticiones_sospechosas(
    archivo: str = "trazas_agente.jsonl",
) -> None:
    """Analiza trazas buscando bucles o herramientas invocadas consecutivamente."""
    try:
        with open(archivo, encoding="utf-8") as f:
            registros = [json.loads(linea) for linea in f]
    except FileNotFoundError:
        print(f"No se encontró '{archivo}'.")
        return

    repeticiones_encontradas = 0
    for registro in registros:
        herramientas_usadas = [a["herramienta"] for a in registro.get("acciones", [])]
        for i in range(1, len(herramientas_usadas)):
            if herramientas_usadas[i] == herramientas_usadas[i - 1]:
                print(f"[ALERTA AUDITORÍA] Sesión {registro['session_id']} usó '{herramientas_usadas[i]}' dos veces consecutivas.")
                repeticiones_encontradas += 1
                break
    if repeticiones_encontradas == 0:
        print("Auditoría de trazas: No se detectaron repeticiones consecutivas sospechosas.")

if __name__ == "__main__":
    print("==========================================================")
    print("EJECUCIÓN DE AGENTE CON SUPERVISIÓN HUMANA Y TRAZAS (B23)")
    print("==========================================================")
    
    # Caso 1: Riesgo bajo (cálculo de costo)
    print("\n--- CASO 1: Consulta de bajo riesgo ---")
    entrada_1 = "¿Cuánto cuesta enviar un paquete de 3kg a 150km?"
    res_1 = ejecutor_agente.invoke({"entrada": entrada_1})
    registrar_traza("sesion_bajo_riesgo", entrada_1, res_1)
    
    # Caso 2: Riesgo alto (solicitud de reembolso monetario)
    print("\n--- CASO 2: Acción de alto riesgo (debe pedir confirmación) ---")
    entrada_2 = "El paquete del pedido AR12345 llegó roto, por favor genera un reembolso de $1200."
    res_2 = ejecutor_agente.invoke({"entrada": entrada_2})
    registrar_traza("sesion_alto_riesgo", entrada_2, res_2)
    
    print("\n==========================================================")
    print("ANÁLISIS DE TRAZAS GUARDADAS EN trazas_agente.jsonl")
    print("==========================================================")
    marcar_repeticiones_sospechosas()
    print("\nRegistro de decisiones de supervisión:", registro_aprobaciones)