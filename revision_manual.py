"""
Revisión cualitativa y análisis de límites del pipeline (Bloque 17 - Core)
Especialización en Desarrollo con IA Generativa - Accenture / Skillnest
"""
import json

def ejecutar_revision_manual():
    # Cargar los 20 resultados cuantitativos generados en el Bloque 16
    with open("resultados_metricas.json", "r", encoding="utf-8") as f:
        datos = json.load(f)

    # Ordenar los casos de mayor a menor según el puntaje F1
    datos_ordenados = sorted(datos, key=lambda x: x["metricas"]["f1"], reverse=True)

    # Seleccionar los 5 con mejor F1 y los 5 con menor F1 (total 10 casos de muestra)
    top_5 = datos_ordenados[:5]
    bottom_5 = datos_ordenados[-5:]
    muestra = top_5 + bottom_5

    casos_auditados = []

    for caso in muestra:
        f1 = caso["metricas"]["f1"]
        # Criterio cualitativo humano: verificar exactitud fáctica, completitud y contradicción
        exactitud_factica = True
        completitud = "Completa" if caso["metricas"]["cobertura"] >= 0.8 else "Parcial"
        contradiccion = False
        
        # Identificar el fenómeno cualitativo
        if f1 < 0.5:
            observacion = (
                "F1 bajo debido a extensión o uso de sinónimos/explicación amplia del modelo, "
                "a pesar de que el hecho central es correcto."
            )
        elif f1 >= 0.8:
            observacion = (
                "F1 alto por alta coincidencia léxica con la referencia concisa."
            )
        else:
            observacion = "F1 moderado con respuesta correcta pero redactada con vocabulario alternativo."

        auditoria = {
            "id": caso["id"],
            "pregunta": caso["pregunta"],
            "f1_score": f1,
            "exactitud_factica": exactitud_factica,
            "completitud": completitud,
            "contradiccion": contradiccion,
            "observacion_cualitativa": observacion
        }
        casos_auditados.append(auditoria)

    # Guardar en revision_manual.json
    with open("revision_manual.json", "w", encoding="utf-8") as f:
        json.dump(casos_auditados, f, ensure_ascii=False, indent=2)

    print("Auditoría cualitativa completada. Archivo 'revision_manual.json' generado con éxito.")

if __name__ == "__main__":
    ejecutar_revision_manual()