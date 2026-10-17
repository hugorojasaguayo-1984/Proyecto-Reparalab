import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()


def armar_peticion(pregunta: str) -> tuple[str, dict, dict]:
    """Valida la entrada y construye los datos necesarios para la petición."""
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")
        
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
    """Envía la petición manejando fallas de conexión y formato JSON."""
    try:
        respuesta = requests.post(url, headers=headers, json=body)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
        
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")


def extraer_texto(datos: dict) -> str:
    """Extrae el texto generado gestionando posibles datos faltantes."""
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def obtener_dato_de_prueba(pregunta: str) -> str:
    """Función principal orquestadora."""
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    pregunta_valida = "Confirma en una frase corta que esta conexión funciona correctamente."   
    try:
        resultado = obtener_dato_de_prueba(pregunta_valida)
        print("Respuesta de Gemini:")
        print(resultado)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)