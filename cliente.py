import os
import time
import random
import requests
from dotenv import load_dotenv
from typing import Callable, Any

# Cargar variables de entorno desde .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = "gemini-3.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

COSTO_POR_1000_TOKENS = 0.002  # Valor referencial por 1,000 tokens según la guía
costo_total_sesion = 0.0


def armar_peticion(pregunta: str, system_instruction: str = "") -> dict:
    """Arma el cuerpo JSON para la petición a Gemini."""
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    cuerpo = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    if system_instruction:
        cuerpo["systemInstruction"] = {
            "parts": [
                {"text": system_instruction}
            ]
        }

    return cuerpo


def enviar_peticion(cuerpo: dict) -> dict:
    """Envía la petición HTTP y clasifica errores (401/403 -> ValueError, 429/500 -> TimeoutError)."""
    try:
        respuesta = requests.post(
            URL, json=cuerpo, headers=headers, timeout=10
        )
    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")

    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")

    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar.")

    respuesta.raise_for_status()
    return respuesta.json()


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    """Reintenta ante TimeoutError con backoff exponencial (2, 4, 8s) y jitter aleatorio."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} falló. Reintentando en {espera_con_jitter:.1f}s...")
            time.sleep(espera_con_jitter)


def extraer_texto(respuesta: dict) -> str:
    """Extrae el texto de la respuesta del modelo."""
    try:
        return respuesta["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def registrar_costo(respuesta: dict) -> float:
    """Lee usageMetadata de la respuesta, calcula el costo y lo acumula en la sesión."""
    global costo_total_sesion
    uso = respuesta.get("usageMetadata", {})
    total_tokens = uso.get("totalTokenCount", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
    print(f"Operación: {total_tokens} tokens, costo estimado: ${costo_estimado:.5f} (acumulado: ${costo_total_sesion:.5f})")
    return costo_estimado


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    """Interfaz pública: orquesta petición, reintento exponencial, registro de costo y extracción."""
    cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    registrar_costo(respuesta)
    return extraer_texto(respuesta)


if __name__ == "__main__":
    print("Iniciando ensayo controlado de 10 peticiones rápidas...\n")
    for i in range(10):
        try:
            respuesta = consultar_modelo(f"Pregunta de prueba número {i}: ¿Cuál es la capital de Chile?")
            print(f"Respuesta {i}: {respuesta[:45]}...")
        except RuntimeError as error:
            print(f"Respuesta {i} falló definitivamente: {error}")

    print(f"\nCosto total acumulado del ensayo: ${costo_total_sesion:.5f}")