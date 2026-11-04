"""
Pruebas unitarias para el pipeline de texto
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.2 - Bloque 15 [Actividad práctica]
"""
import pytest
from pipeline_texto import limpiar_texto, tokenizar, procesar_texto, vectorizar

def test_limpiar_texto_elimina_puntuacion_y_minusculas():
    texto = "¡Hola, Mundo! ¿Cómo estás?"
    esperado = "hola mundo cómo estás"
    assert limpiar_texto(texto) == esperado

def test_limpiar_texto_vacio():
    assert limpiar_texto("") == ""
    assert limpiar_texto(None) == ""

def test_tokenizar_separa_por_espacios():
    texto = "la capital de chile es santiago"
    esperado = ["la", "capital", "de", "chile", "es", "santiago"]
    assert tokenizar(texto) == esperado

def test_tokenizar_vacio():
    assert tokenizar("") == []

def test_procesar_texto_pipeline_completo():
    texto = "¡Santiago es la capital de Chile!"
    esperado = ["santiago", "es", "la", "capital", "de", "chile"]
    assert procesar_texto(texto) == esperado

def test_vectorizar_cuenta_frecuencias():
    tokens = ["gato", "perro", "gato", "gato"]
    conteo = vectorizar(tokens)
    assert conteo["gato"] == 3
    assert conteo["perro"] == 1