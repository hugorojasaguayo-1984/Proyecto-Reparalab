"""
Pipeline de procesamiento de texto y cálculo de métricas (NLP básico)
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.2 - Bloques 15 y 16: Limpieza, tokenización y métricas (P, R, F1)
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


def contar_coincidencias(tokens_ref: list[str], tokens_resp: list[str]) -> int:
    """
    Cuenta cuántas palabras coinciden considerando repeticiones reales
    mediante la intersección de frecuencias de Counter (&).
    """
    conteo_ref = Counter(tokens_ref)
    conteo_resp = Counter(tokens_resp)
    interseccion = conteo_ref & conteo_resp
    return sum(interseccion.values())


def calcular_precision_cobertura_f1(tokens_ref: list[str], tokens_resp: list[str]) -> tuple[float, float, float]:
    """
    Calcula Precisión, Cobertura (Recall) y puntaje F1 entre dos listas de tokens.
    """
    if not tokens_ref or not tokens_resp:
        return 0.0, 0.0, 0.0

    coincidencias = contar_coincidencias(tokens_ref, tokens_resp)

    # Precisión: coincidencias / total de tokens emitidos por la respuesta
    precision = coincidencias / len(tokens_resp)
    # Cobertura: coincidencias / total de tokens requeridos por la referencia
    cobertura = coincidencias / len(tokens_ref)

    # Promedio armónico F1
    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * (precision * cobertura) / (precision + cobertura)

    return precision, cobertura, f1


def calcular_metricas(texto_ref: str, texto_resp: str) -> dict:
    """
    Recibe texto de referencia humana y texto de respuesta del modelo,
    ejecuta el pipeline de procesamiento y devuelve un diccionario con las métricas.
    """
    t_ref = procesar_texto(texto_ref)
    t_resp = procesar_texto(texto_resp)

    p, r, f1 = calcular_precision_cobertura_f1(t_ref, t_resp)

    return {
        "tokens_referencia": len(t_ref),
        "tokens_respuesta": len(t_resp),
        "coincidencias": contar_coincidencias(t_ref, t_resp),
        "precision": round(p, 4),
        "cobertura": round(r, 4),
        "f1": round(f1, 4)
    }


if __name__ == "__main__":
    referencia = "Santiago es la capital de Chile"
    respuesta = "La capital de Chile es Santiago oficialmente"

    resultado = calcular_metricas(referencia, respuesta)

    print("=== Cálculo de Métricas (Bloque 16) ===")
    print(f"Texto Referencia : {referencia}")
    print(f"Texto Respuesta  : {respuesta}")
    print(f"Tokens Ref ({resultado['tokens_referencia']}), Tokens Resp ({resultado['tokens_respuesta']}), Coincidencias: {resultado['coincidencias']}")
    print(f"Precisión : {resultado['precision'] * 100:.2f}%")
    print(f"Cobertura : {resultado['cobertura'] * 100:.2f}%")
    print(f"F1-Score  : {resultado['f1'] * 100:.2f}%")