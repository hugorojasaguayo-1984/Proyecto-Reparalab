"""
Suite completa de pruebas de orquestación, bifurcación y tolerancia a fallos
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.3 - Bloque 20: Checklist integral de orquestación [Actividad core]
"""
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from enrutamiento import (
    construir_paso_clasificacion,
    construir_cadena_con_enrutamiento,
    construir_cadena_queja_segura,
    procesar_mensaje_seguro,
)

# --------------------------------------------------------------------------
# 1. Pruebas de Clasificación y Normalización
# --------------------------------------------------------------------------
def test_clasificacion_normaliza_antes_de_comparar():
    """
    Verifica que el paso de clasificación limpie espacios y mayúsculas
    usando .strip().lower() sin importar cómo responda el modelo.
    """
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Queja \n")

    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"mensaje": "algo salió mal"}
    )
    assert resultado == "queja"


def test_clasificacion_usa_fallback_ante_fallo_del_modelo():
    """
    Verifica que si el clasificador falla por error de red o API, su propio
    with_fallbacks devuelva la categoría por defecto ('pregunta') sin caerse.
    """
    def fallar_clasificacion(x):
        raise ConnectionError("Fallo simulado en el servicio de clasificación")

    modelo_roto = RunnableLambda(fallar_clasificacion)
    resultado = construir_paso_clasificacion(modelo_roto).invoke(
        {"mensaje": "mensaje de prueba"}
    )
    assert resultado == "pregunta"


# --------------------------------------------------------------------------
# 2. Pruebas de Bifurcación de Rutas (RunnableBranch)
# --------------------------------------------------------------------------
def test_enrutamiento_va_a_cadena_queja():
    """
    Verifica que un mensaje clasificado como 'queja' dirija el flujo a cadena_queja.
    """
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "queja"
    cadena_queja_falsa = MagicMock()
    cadena_queja_falsa.return_value = "respuesta empática de queja"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=cadena_queja_falsa,
    )
    resultado = cadena.invoke({"mensaje": "el servicio está fallando"})

    assert cadena_queja_falsa.called
    assert resultado == "respuesta empática de queja"


def test_enrutamiento_va_a_cadena_pregunta():
    """
    Verifica que un mensaje clasificado como 'pregunta' dirija el flujo a cadena_pregunta.
    """
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "pregunta"
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta técnica precisa"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "¿cómo configuro mi perfil?"})

    assert cadena_pregunta_falsa.called
    assert resultado == "respuesta técnica precisa"


def test_enrutamiento_usa_default_ante_categoria_desconocida():
    """
    Verifica que ante una categoría no prevista por el modelo, el flujo
    no se rompa y caiga ordenadamente en la ruta por defecto (cadena_pregunta).
    """
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "categoria_inventada"
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta de ruta por defecto"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "mensaje de intención ambigua"})

    assert cadena_pregunta_falsa.called
    assert resultado == "respuesta de ruta por defecto"


# --------------------------------------------------------------------------
# 3. Pruebas de Resiliencia: with_fallbacks en ruta de destino
# --------------------------------------------------------------------------
def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    """
    Simula una excepción de red en la ruta de queja y verifica que with_fallbacks
    active la alternativa configurada, entregando una respuesta razonable sin fallar.
    """
    def fallar_a_proposito(x):
        raise ConnectionError("Fallo simulado de conexión con la API")

    cadena_queja_falsa = RunnableLambda(fallar_a_proposito)
    cadena_queja_segura = construir_cadena_queja_segura(cadena_queja_falsa)

    resultado = cadena_queja_segura.invoke({"mensaje": "esto no funciona"})

    assert "equipo" in resultado.lower() or "soporte" in resultado.lower()


# --------------------------------------------------------------------------
# 4. Pruebas de Resiliencia: Red de seguridad general try/except
# --------------------------------------------------------------------------
def test_procesar_mensaje_seguro_no_propaga_excepciones():
    """
    Simula un fallo catastrófico no previsto en la cadena completa y confirma
    que procesar_mensaje_seguro capture el error y devuelva un mensaje seguro.
    """
    def fallar_cadena_completa(x):
        raise RuntimeError("Fallo crítico e imprevisto en la infraestructura")

    cadena_rota = RunnableLambda(fallar_cadena_completa)
    resultado = procesar_mensaje_seguro(cadena_rota, "mensaje de prueba")

    assert "no pudimos procesar" in resultado.lower()