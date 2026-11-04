"""
Pipeline de procesamiento de texto (NLP básico)
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.2 - Bloque 15: Pipeline modular de limpieza y tokenización
"""
import re
from collections import Counter

def limpiar_texto(texto: str) -> str:
    """
    Convierte el texto a minúsculas y elimina signos de puntuación y caracteres especiales,
    conservando letras, números y espacios.
    """
    if not texto:
        return ""
    texto_min = texto.lower()
    texto_limpio = re.sub(r'[^\w\s]', '', texto_min)
    return texto_limpio.strip()

def tokenizar(texto: str) -> list[str]:
    """
    Divide un texto limpio en una lista de palabras (tokens) separadas por espacios.
    """
    if not texto:
        return []
    return texto.split()

def procesar_texto(texto: str) -> list[str]:
    """
    Ejecuta el pipeline completo: limpieza y posterior tokenización.
    """
    limpio = limpiar_texto(texto)
    return tokenizar(limpio)

def vectorizar(tokens: list[str]) -> Counter:
    """
    Convierte una lista de tokens en un conteo de frecuencias utilizando Counter.
    """
    return Counter(tokens)

if __name__ == "__main__":
    texto = "¡Hola! Este es el pipeline de procesamiento de texto de la Unidad 2."
    tokens = procesar_texto(texto)
    print(f"Texto de prueba: {texto}")
    print(f"Tokens generados: {tokens}")
    print(f"Total de tokens: {len(tokens)}")