import os
import time
import re
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def armar_peticion(pregunta_usuario: str, system_instruction: str = None, response_schema: dict = None) -> tuple[str, dict, dict]:
    """Arma la petición con prompt de sistema y schema opcional (Página 3 de la guía)."""
    if not pregunta_usuario or not pregunta_usuario.strip():
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
                    {"text": pregunta_usuario}
                ]
            }
        ]
    }

    if system_instruction:
        body["systemInstruction"] = {
            "parts": [
                {"text": system_instruction}
            ]
        }

    if response_schema:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }

    return url, headers, body


def enviar_peticion(url: str, headers: dict, body: dict) -> dict:
    """Envía la petición HTTP POST a Gemini con reintento ante alta demanda temporal."""
    for intento in range(3):
        try:
            respuesta = requests.post(url, headers=headers, json=body)
            datos = respuesta.json()
            if datos.get("error", {}).get("code") == 503:
                time.sleep(2)
                continue
            return datos
        except requests.exceptions.ConnectionError:
            if intento == 2:
                raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
            time.sleep(2)
        except requests.exceptions.JSONDecodeError:
            raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")
    return datos


def extraer_texto(datos: dict) -> str:
    """Extrae el texto generado."""
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        if "error" in datos:
            raise RuntimeError(f"Google devolvió: {datos['error'].get('message', 'Error desconocido')}")
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def parsear_respuesta_json(texto: str) -> dict:
    """Limpia markdown y convierte a diccionario JSON (Página 5 de la guía)."""
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")
    return datos


# =====================================================================
# EJEMPLO EXACTO DE LA GUÍA (Páginas 5 y 6 de la Lección 10-2)
# =====================================================================
if __name__ == "__main__":
    pregunta_usuario = "Necesito ayuda para resetear mi contraseña, no me llega el correo de verificación"

    system_instruction = (
        "Responde únicamente con un objeto JSON válido, sin texto adicional "
        "y sin usar bloques de markdown. El JSON debe tener exactamente estas "
        "claves: 'categoria' (string) y 'confianza' (número entre 0 y 1)."
    )

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "categoria": {"type": "STRING"},
            "confianza": {"type": "NUMBER"}
        },
        "required": ["categoria", "confianza"]
    }

    try:
        url, headers, body = armar_peticion(pregunta_usuario, system_instruction)
        respuesta_json = enviar_peticion(url, headers, body)
        texto = extraer_texto(respuesta_json)
        datos = parsear_respuesta_json(texto)

        print("Resultado JSON interpretado:")
        print(datos)
        print("Tipo de dato en Python:")
        print(type(datos))

    except (ValueError, RuntimeError) as error:
        print("Error en la ejecución:", error)