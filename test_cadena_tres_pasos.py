"""
Pruebas unitarias para la cadena de tres pasos de LangChain
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.3 - Bloque 18 [Actividad práctica]
"""
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from cadena_tres_pasos import construir_cadena

def test_cadena_conecta_los_tres_pasos():
    # Modelo simulado (mock) con side_effect para simular las 3 respuestas en secuencia
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="punto 1\npunto 2\npunto 3"),
        AIMessage(content="texto simplificado"),
        AIMessage(content="- viñeta 1\n- viñeta 2"),
    ]

    # Construir la cadena inyectando el mock en vez del modelo real
    cadena = construir_cadena(modelo_falso)

    # Invocar la cadena
    resultado = cadena.invoke({"texto": "texto de prueba"})

    # Verificaciones exigidas por la guía
    assert modelo_falso.call_count == 3
    assert "viñeta" in resultado