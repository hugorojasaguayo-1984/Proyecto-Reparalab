"""
Enrutamiento condicional según el tipo de entrada
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.3 - Bloque 19: Clasificación y bifurcación con RunnableBranch
"""
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableBranch,
    RunnablePassthrough,
)

# 1. Plantilla de clasificación
plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola palabra: "
    "pregunta, queja o sugerencia. Responde solo con esa palabra.\n\n{mensaje}"
)

# 2. Las tres rutas posibles especializadas
plantilla_pregunta = PromptTemplate.from_template(
    "Responde esta pregunta técnica con precisión:\n\n{mensaje}"
)

plantilla_queja = PromptTemplate.from_template(
    "Responde a esta queja con empatía, reconociendo el problema antes de ofrecer una solución:\n\n{mensaje}"
)

plantilla_sugerencia = PromptTemplate.from_template(
    "Agradece esta sugerencia y explica cómo se evaluará dentro del producto:\n\n{mensaje}"
)

def construir_paso_clasificacion(modelo):
    """
    Construye el paso clasificador normalizando la salida a minúsculas y sin espacios.
    """
    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )

def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):
    """
    Construye la bifurcación condicional usando RunnableBranch.
    Permite inyectar mocks en pruebas unitarias.
    """
    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()

    # Bifurcación condicional: prueba las condiciones en orden
    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta,  # Ruta por defecto
    )

    return (
        RunnablePassthrough.assign(categoria=paso_clasificacion)
        | bifurcacion
    )

if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)

    # Construir las 3 cadenas reales
    c_pregunta = plantilla_pregunta | modelo | StrOutputParser()
    c_queja = plantilla_queja | modelo | StrOutputParser()
    c_sugerencia = plantilla_sugerencia | modelo | StrOutputParser()

    paso_clasif = construir_paso_clasificacion(modelo)
    cadena_enrutada = construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasif,
        cadena_queja=c_queja,
        cadena_sugerencia=c_sugerencia,
        cadena_pregunta=c_pregunta,
    )

    mensaje_prueba = "La app se cierra cada vez que subo una foto."
    print(f"Mensaje entrante: '{mensaje_prueba}'")
    print("Enrutando y ejecutando...")
    resultado = cadena_enrutada.invoke({"mensaje": mensaje_prueba})
    print("\n=== Respuesta de la Ruta Elegida ===")
    print(resultado)