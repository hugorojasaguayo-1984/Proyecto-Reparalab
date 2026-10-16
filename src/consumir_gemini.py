import os
import requests
from dotenv import load_dotenv

# Carga la clave desde el archivo .env
load_dotenv()


def obtener_dato_de_prueba(pregunta: str) -> str:
    # Lee la variable que pusiste en el .env
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.5-flash"
    
    # La URL exacta que funcionó en Thunder Client
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
    
    respuesta = requests.post(url, headers=headers, json=body)
    datos = respuesta.json()
    
    if "error" in datos:
        print("Detalle del error:", datos["error"])
        return "Error en la petición"
        
    return datos["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    pregunta = "Confirma en una frase corta que esta conexión funciona correctamente."
    print("Respuesta de Gemini:")
    print(obtener_dato_de_prueba(pregunta))