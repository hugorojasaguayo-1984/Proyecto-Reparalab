"""
Flujo orquestado con enrutamiento condicional y resiliencia multicapa
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.3 - Bloques 19 y 20: Clasificación protegida, bifurcación, fallbacks y try/except [Actividad core]
"""
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableBranch,
    RunnablePassthrough,
    RunnableLambda,
)

# 1. Plantilla de clasificación de intención
plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola palabra: "
    "pregunta, queja o sugerencia. Responde solo con esa palabra.\n\n{mensaje}"
)

# 2. Plantillas especializadas por cada categoría de destino
plantilla_pregunta = PromptTemplate.from_template(
    "Responde esta pregunta técnica con precisión:\n\n{mensaje}"
)

plantilla_queja = PromptTemplate.from_template(
    "Responde a esta queja con empatía, reconociendo el problema antes de ofrecer una solución:\n\n{mensaje}"
)

plantilla_sugerencia = PromptTemplate.from_template(
    "Agradece esta sugerencia y explica cómo se evaluará dentro del producto:\n\n{mensaje}"
)

# 3. Fallbacks con respuestas razonables (no son mensajes de error genéricos)
# Fallback para cuando falla el paso de clasificación: asume la ruta por defecto ("pregunta")
fallback_clasificacion = RunnableLambda(lambda _: "pregunta")

# Fallback para cuando falla la ruta de queja: ofrece contención y contacto humano
respuesta_generica_queja = RunnableLambda(
    lambda x: (
        "Lamentamos el inconveniente. Tu solicitud ha sido registrada y un miembro "
        "de nuestro equipo de soporte se pondrá en contacto contigo a la brevedad."
    )
)


def construir_paso_clasificacion(modelo):
    """
    Construye el clasificador normalizando la salida a minúsculas y sin espacios.
    Protegido con with_fallbacks: si la llamada falla, devuelve la categoría por defecto 'pregunta'.
    """
    clasificador_base = (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )
    return clasificador_base.with_fallbacks([fallback_clasificacion])


def construir_cadena_queja_segura(cadena_queja):
    """
    Protege la ruta de queja mediante with_fallbacks.
    Si el modelo principal falla, devuelve la respuesta de respaldo razonable.
    """
    return cadena_queja.with_fallbacks([respuesta_generica_queja])


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):
    """
    Construye la bifurcación condicional conectando las rutas mediante RunnableBranch.
    Permite la inyección de rutas alternativas o mocks en pruebas unitarias.
    """
    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()

    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta,  # Ruta por defecto ante categorías no previstas o fallos
    )

    return (
        RunnablePassthrough.assign(categoria=paso_clasificacion)
        | bifurcacion
    )


def procesar_mensaje_seguro(cadena, mensaje: str) -> str:
    """
    Función de entrada con try/except alrededor de .invoke().
    Registra el fallo operativo y asegura que ningún error tumbe el flujo sin respuesta.
    """
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        # Registro explícito del error para trazabilidad y monitoreo
        print(f"[REGISTRO OPERACIONAL]: Error al procesar mensaje en el flujo: {error}")
        return (
            "No pudimos procesar tu mensaje en este momento. "
            "Por favor, intenta de nuevo más tarde."
        )


if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)

    # Construir las cadenas especializadas
    c_pregunta = plantilla_pregunta | modelo | StrOutputParser()
    c_queja_base = plantilla_queja | modelo | StrOutputParser()
    c_queja_protegida = construir_cadena_queja_segura(c_queja_base)
    c_sugerencia = plantilla_sugerencia | modelo | StrOutputParser()

    # Clasificador con fallback incorporado
    paso_clasif = construir_paso_clasificacion(modelo)

    # Flujo orquestado con bifurcación
    cadena_completa = construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasif,
        cadena_queja=c_queja_protegida,
        cadena_sugerencia=c_sugerencia,
        cadena_pregunta=c_pregunta,
    )

    mensaje_usuario = "La app se cierra sola cada vez que intento guardar."
    print(f"Mensaje entrante: '{mensaje_usuario}'")
    print("Procesando a través del flujo orquestado seguro...")

    respuesta = procesar_mensaje_seguro(cadena_completa, mensaje_usuario)
    print("\n=== Respuesta Obtenida ===")
    print(respuesta)