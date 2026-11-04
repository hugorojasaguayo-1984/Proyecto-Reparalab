"""
Cadena de tres pasos encadenados con LangChain
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
Unidad U2.3 - Bloque 18 [Actividad práctica]
"""
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def construir_cadena(modelo):
    """
    Construye y devuelve una chain de tres pasos encadenados con el operador '|'.
    Recibe el modelo como parámetro para permitir pruebas con mocks.
    """
    # Paso 1: Extraer los puntos clave
    plantilla_extraccion = PromptTemplate.from_template(
        "Lee el siguiente texto y devuelve solo sus 3 puntos clave, "
        "uno por línea, sin desarrollarlos:\n\n{texto}"
    )
    paso_extraccion = plantilla_extraccion | modelo | StrOutputParser()

    # Paso 2: Reescribir en lenguaje simple
    plantilla_simplificacion = PromptTemplate.from_template(
        "Reescribe estos puntos en lenguaje simple, sin jerga técnica, "
        "para alguien sin conocimientos previos:\n\n{puntos}"
    )
    paso_simplificacion = plantilla_simplificacion | modelo | StrOutputParser()

    # Paso 3: Formatear como lista de viñetas
    plantilla_formato = PromptTemplate.from_template(
        "Convierte este texto en una lista de viñetas markdown, "
        "de máximo 3 líneas, sin introducción:\n\n{texto_simple}"
    )
    paso_formato = plantilla_formato | modelo | StrOutputParser()

    # Encadenamiento con funciones intermedias lambda para adaptar las claves
    cadena = (
        paso_extraccion
        | (lambda puntos: {"puntos": puntos})
        | paso_simplificacion
        | (lambda texto_simple: {"texto_simple": texto_simple})
        | paso_formato
    )
    return cadena

if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)
    cadena = construir_cadena(modelo)

    texto_entrada = (
        "Los modelos de lenguaje grandes aprenden patrones a partir de grandes cantidades "
        "de texto durante su entrenamiento, pero no almacenan copias exactas. En cambio, "
        "aprenden relaciones estadísticas entre palabras y conceptos, lo que les permite "
        "generar nuevo texto sin reproducir literalmente sus datos de entrenamiento."
    )

    print("Iniciando ejecución de la cadena de 3 pasos...")
    resultado = cadena.invoke({"texto": texto_entrada})
    print("\n=== Resultado Final de la Cadena ===")
    print(resultado)