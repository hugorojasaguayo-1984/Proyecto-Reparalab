"""
Pruebas unitarias para el flujo con enrutamiento condicional
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.3 - Bloque 19: Cobertura completa de bifurcación con Mocks
"""
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
)

def test_clasificacion_normaliza_antes_de_comparar():
    """
    Verifica que la clasificación normalice a minúsculas y sin espacios.
    """
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Queja \n")
    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"mensaje": "algo salió mal"}
    )
    assert resultado == "queja"

def test_enrutamiento_va_a_cadena_queja():
    """
    Verifica que un mensaje clasificado como 'queja' ejecute la ruta cadena_queja.
    """
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "queja"
    cadena_queja_falsa = MagicMock()
    cadena_queja_falsa.return_value = "respuesta de queja"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=cadena_queja_falsa,
    )
    resultado = cadena.invoke({"mensaje": "esto no funciona nunca"})

    assert cadena_queja_falsa.called
    assert resultado == "respuesta de queja"

def test_enrutamiento_va_a_cadena_pregunta():
    """
    Verifica que un mensaje clasificado como 'pregunta' ejecute la ruta cadena_pregunta.
    """
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "pregunta"
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta de pregunta"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "¿cómo cambio mi contraseña?"})

    assert cadena_pregunta_falsa.called
    assert resultado == "respuesta de pregunta"

def test_enrutamiento_usa_default_ante_categoria_desconocida():
    """
    Verifica que una categoría inesperada caiga en la ruta por defecto (cadena_pregunta).
    """
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "categoria_inventada"
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta por defecto"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "mensaje ambiguo"})

    assert cadena_pregunta_falsa.called
    assert resultado == "respuesta por defecto"