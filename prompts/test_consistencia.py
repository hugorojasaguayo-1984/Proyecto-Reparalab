import json
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json
from prompts.banco import BANCO_DE_PROMPTS

registro = {}

for prompt in BANCO_DE_PROMPTS:
    nombre = prompt["nombre"]
    exitos = 0
    intentos = 3

    for intento in range(intentos):
        url, headers, body = armar_peticion(
            prompt["ejemplo_usuario"],
            prompt["system_instruction"],
            prompt.get("response_schema"),
        )
        try:
            respuesta = enviar_peticion(url, headers, body)
            texto = extraer_texto(respuesta)
            datos = parsear_respuesta_json(texto)
            if all(clave in datos for clave in prompt["claves_esperadas"]):
                exitos += 1
        except Exception:
            pass

        time.sleep(3)

    print(f"{nombre}: {exitos}/{intentos} respuestas válidas")
    registro[nombre] = {"exitos": exitos, "intentos": intentos}

    ruta_registro = os.path.join(os.path.dirname(__file__), "registro_resultados.json")
    with open(ruta_registro, "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)

print("\nPrueba finalizada con éxito.")
print("Evidencia guardada en: prompts/registro_resultados.json")