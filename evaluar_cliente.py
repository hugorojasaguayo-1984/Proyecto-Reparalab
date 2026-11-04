"""
Evaluación de salidas del cliente y cálculo de métricas (Bloque 16)
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
"""
import json
import os
from pipeline_texto import calcular_metricas
from cliente import consultar_modelo

# Banco de 20 casos de prueba con preguntas y respuestas humanas de referencia
CASOS_EVALUACION = [
    {"id": 1, "pregunta": "¿Cuál es la capital de Chile?", "referencia": "La capital de Chile es Santiago."},
    {"id": 2, "pregunta": "¿Cuál es la capital de Argentina?", "referencia": "La capital de Argentina es Buenos Aires."},
    {"id": 3, "pregunta": "¿Cuál es la capital de Perú?", "referencia": "La capital de Perú es Lima."},
    {"id": 4, "pregunta": "¿En qué continente está Francia?", "referencia": "Francia se encuentra en el continente europeo."},
    {"id": 5, "pregunta": "¿Qué idioma oficial se habla en Brasil?", "referencia": "El idioma oficial de Brasil es el portugués."},
    {"id": 6, "pregunta": "¿Quién escribió Don Quijote de la Mancha?", "referencia": "Don Quijote fue escrito por Miguel de Cervantes."},
    {"id": 7, "pregunta": "¿Cuál es el río más largo del mundo?", "referencia": "El río Amazonas es el más largo del mundo."},
    {"id": 8, "pregunta": "¿Cuál es el planeta más cercano al Sol?", "referencia": "Mercurio es el planeta más cercano al Sol."},
    {"id": 9, "pregunta": "¿Qué gas respiramos principalmente para sobrevivir?", "referencia": "Los seres humanos respiramos oxígeno para vivir."},
    {"id": 10, "pregunta": "¿Cuántos días tiene un año bisiesto?", "referencia": "Un año bisiesto tiene 366 días en total."},
    {"id": 11, "pregunta": "¿Cuál es el océano más grande del planeta?", "referencia": "El océano Pacífico es el más extenso del planeta."},
    {"id": 12, "pregunta": "¿En qué país se encuentran las pirámides de Giza?", "referencia": "Las pirámides de Giza se encuentran en Egipto."},
    {"id": 13, "pregunta": "¿Cuál es el metal más liviano de la tabla periódica?", "referencia": "El litio es el metal más liviano que existe."},
    {"id": 14, "pregunta": "¿Cuál es el símbolo químico del agua?", "referencia": "El símbolo químico de la molécula del agua es H2O."},
    {"id": 15, "pregunta": "¿Quién pintó la Mona Lisa?", "referencia": "La Mona Lisa fue pintada por Leonardo da Vinci."},
    {"id": 16, "pregunta": "¿Cuál es la moneda oficial de Japón?", "referencia": "La moneda oficial de Japón es el yen."},
    {"id": 17, "pregunta": "¿Qué instrumento musical tiene 88 teclas?", "referencia": "El piano estándar cuenta con un total de 88 teclas."},
    {"id": 18, "pregunta": "¿Cuál es el hueso más largo del cuerpo humano?", "referencia": "El fémur es el hueso más largo del cuerpo humano."},
    {"id": 19, "pregunta": "¿Cuál es el país más grande del mundo por superficie?", "referencia": "Rusia es el país más grande del mundo por territorio."},
    {"id": 20, "pregunta": "¿A qué temperatura hierve el agua a nivel del mar?", "referencia": "El agua hierve a 100 grados Celsius a nivel del mar."}
]

def ejecutar_evaluacion_completa():
    print("Iniciando evaluación cuantitativa de 20 casos reales...")
    resultados = []

    for caso in CASOS_EVALUACION:
        print(f"Evaluando caso {caso['id']}/20: {caso['pregunta']}")
        
        # Consultar al modelo real mediante cliente.py
        try:
            respuesta_modelo = consultar_modelo(caso['pregunta'])
        except Exception as e:
            respuesta_modelo = f"Error en consulta: {e}"

        # Calcular métricas automáticas comparando contra la referencia humana
        metricas = calcular_metricas(caso['referencia'], respuesta_modelo)

        registro = {
            "id": caso["id"],
            "pregunta": caso["pregunta"],
            "referencia": caso["referencia"],
            "respuesta_modelo": respuesta_modelo,
            "metricas": metricas
        }
        resultados.append(registro)

    # Guardar en archivo JSON según lo exige la guía del Bloque 16
    ruta_salida = "resultados_metricas.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"\nEvaluación finalizada. Resultados guardados exitosamente en '{ruta_salida}'.")

if __name__ == "__main__":
    ejecutar_evaluacion_completa()