import os
import requests
from dotenv import load_dotenv

# Cargar la clave desde el .env
load_dotenv()


def construir_peticion(pregunta: str) -> tuple[str, dict, dict]:
    """Arma la URL, los headers y el body tal como los configuraste en Thunder Client."""
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-2.5-flash"  # O el nombre exacto que pusiste en Thunder Client
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    body = {
        "contents": [
            {"parts": [{"text": pregunta}]}
        ]
    }
    return url, headers, body


def enviar_peticion(url: str, headers: dict, body: dict) -> dict:
    """Envía la petición POST externa y devuelve el JSON."""
    respuesta = requests.post(url, headers=headers, json=body)
    return respuesta.json()


def extraer_texto(datos: dict) -> str:
    """Extrae el texto generado por Gemini."""
    return datos["candidates"][0]["content"]["parts"][0]["text"]


def consultar_modelo(pregunta: str) -> str:
    """Función orquestadora principal."""
    url, headers, body = construir_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    pregunta = "Confirma en una frase corta que esta conexión funciona correctamente."
    print("Respuesta de Gemini:")
    print(consultar_modelo(pregunta))