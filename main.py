"""
Punto de entrada principal (main.py)
Miniaplicación de consumo de API de IA Generativa
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Importar las funciones modulares desde src/consumir_gemini.py
from src.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto

def main():
    prompt = "¿Cuál es la capital de Chile?"
    
    try:
        url, headers, payload = armar_peticion(prompt)
        respuesta_json = enviar_peticion(url, headers, payload)
        texto = extraer_texto(respuesta_json)
        
        print(f"Respuesta del modelo: {texto}")
        print("Proceso terminado sin errores.")
    except Exception as e:
        print(f"Error durante la ejecución: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()