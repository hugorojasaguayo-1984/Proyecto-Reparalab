import os
import time
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


def armar_peticion(pregunta: str, system_instruction: str = "") -> dict:
    """Arma el diccionario del cuerpo JSON para la petición a Gemini."""
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
    """Envía la petición HTTP POST y clasifica los errores según su código de estado."""
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
    espera_segundos: int = 2,
) -> Any:
    """Ejecuta una función reintentando ante TimeoutError."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando...")
            time.sleep(espera_segundos)


def extraer_texto(respuesta: dict) -> str:
    """Extrae el texto generado de la respuesta de Gemini."""
    try:
        return respuesta["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    """Punto de entrada único: arma, envía con reintento, extrae texto y maneja excepciones."""
    cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    return extraer_texto(respuesta)


if __name__ == "__main__":
    try:
        resultado = consultar_modelo("¿Cuál es la capital de Chile?")
        print("Respuesta del modelo:")
        print(resultado)
    except ValueError as error:
        print(f"Error de configuración: {error}")
    except RuntimeError as error:
        print(f"El servicio no respondió tras varios intentos: {error}")