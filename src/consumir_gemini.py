import os
import requests
from dotenv import load_dotenv

# Cargar las credenciales desde el entorno
load_dotenv()


def construir_peticion(pregunta: str) -> tuple[str, dict, dict]:
    """Responsabilidad 1: Construir la URL, headers y body de la petición."""
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }
    return url, headers, body


def enviar_peticion(url: str, headers: dict, body: dict) -> dict:
    """Responsabilidad 2: Enviar la petición HTTP POST externa."""
    respuesta = requests.post(url, headers=headers, json=body)
    return respuesta.json()


def extraer_texto(datos: dict) -> str:
    """Responsabilidad 3: Extraer el contenido textual generado por el modelo."""
    if "error" in datos:
        print("\nDetalle del error devuelto por la API:", datos["error"])
        return "Error en la petición"
        
    return datos["candidates"][0]["content"]["parts"][0]["text"]


def consultar_modelo(pregunta: str) -> str:
    """Responsabilidad 4: Orquestar el flujo llamando a las funciones especializadas."""
    url, headers, body = construir_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    # Prueba local de ejecución controlada
    pregunta_prueba = "Confirma en una frase corta que esta conexión funciona correctamente."
    print("Respuesta de Gemini:")
    print(consultar_modelo(pregunta_prueba))