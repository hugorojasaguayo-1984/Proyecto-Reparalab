import os
import time
import requests
from dotenv import load_dotenv

# Cargar la clave desde el archivo .env
load_dotenv()


def armar_peticion(pregunta: str) -> tuple[str, dict, dict]:
    """1. Valida la pregunta y arma la URL, headers y body."""
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
    """2. Envía la petición a Google y devuelve la respuesta en JSON."""
    try:
        respuesta = requests.post(url, headers=headers, json=body)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
        
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")


def extraer_texto(datos: dict) -> str:
    """3. Saca el texto escrito por Gemini dentro del JSON."""
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def calcular_costo(datos: dict, precio_entrada: float, precio_salida: float) -> float:
    """4. Lee los tokens usados en usageMetadata y calcula el costo en dólares."""
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    tokens_salida = uso["candidatesTokenCount"]
    return (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)


def obtener_dato_de_prueba(pregunta: str) -> str:
    """Función principal que une el flujo."""
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


# =====================================================================
# BLOQUE 9 (Página 3 de la guía): Medición de latencia real (4 intentos)
# =====================================================================
if __name__ == "__main__":
    pregunta_prueba = "Confirma en una frase corta que esta conexión funciona correctamente."
    latencias = []

    print("--- Midiendo latencia real de Gemini 1.5 Flash (4 intentos) ---")
    
    try:
        for i in range(4):
            inicio = time.perf_counter()
            resultado = obtener_dato_de_prueba(pregunta_prueba)
            fin = time.perf_counter()
            
            demora = fin - inicio
            latencias.append(demora)
            print(f"Intento {i + 1}: {demora:.2f} segundos")
            time.sleep(1)  # Pausa de 1 segundo recomendada por la guía
            
        promedio = sum(latencias) / len(latencias)
        print(f"\n--> Latencia promedio observada: {promedio:.2f} segundos")
        print(f"Respuesta del modelo: {resultado}")
        
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)