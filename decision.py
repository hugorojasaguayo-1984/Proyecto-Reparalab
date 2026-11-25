# Bloque 30 - Actividad Core: Metodo de decision y generacion de decision_personalizacion.md


def recomendar_estrategia(respuestas: dict[str, bool]) -> tuple[dict[str, int], list[str]]:
    """Puntua RAG, Fine-tuning completo y PEFT segun las 5 preguntas de criterio."""
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3
    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1
    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1
    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1
    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    maximo = max(puntos.values())
    ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
    return puntos, ganadoras


# Paso 1: Respuestas basadas en evidencia real de nuestro proyecto
respuestas_mi_caso = {
    "informacion_cambia_seguido": True,          # Las tarifas y reglas de envios en vectorstore/ se actualizan mensualmente
    "problema_de_formato_o_tono": True,          # El enrutador/normalizador requiere JSON estricto {"categoria", "requiere_aprobacion"}
    "dataset_grande_y_de_calidad": False,        # Solo tenemos 12 ejemplos validados en dataset_tuning.py (umbral: >= 200)
    "presupuesto_limitado_o_iterar_rapido": True, # Usamos cuota gratuita/limitada de Gemini API y necesitamos iterar en minutos
    "necesita_multiples_variantes": False,       # Un unico asistente unificado en espanol para toda la operacion
}


def generar_documento_decision(problema: str, puntos: dict[str, int], ganadoras: list[str]) -> str:
    """Construye el documento Markdown completo con las 4 secciones exigidas por la rubrica."""
    empate = len(ganadoras) > 1
    lineas = [
        "# Decision de personalizacion: asistente de operaciones y logistica",
        "",
        "## 1. El problema",
        problema,
        "",
        "## 2. Resultado del metodo de decision",
    ]
    for tecnica, p in sorted(puntos.items(), key=lambda x: -x[1]):
        lineas.append(f"- {tecnica}: {p} puntos")
    if empate:
        lineas.append("")
        lineas.append(f"**Empate entre: {', '.join(ganadoras)}**")

    lineas.extend([
        "",
        "## 3. Tecnica elegida y por que",
        (
            "Elijo **RAG** como tecnica principal inmediata (ganadora clara con 5 puntos frente a 3 de PEFT "
            "y 1 de Fine-tuning completo). Las tarifas, estados de pedidos y reglas operativas cambian "
            "periodicamente, por lo que reindexar documentos en Chroma toma segundos y no requiere reentrenar "
            "ni pagar trabajos de tuning. Descarto Fine-tuning completo y PEFT en esta etapa porque solo "
            "contamos con 12 ejemplos etiquetados (muy por debajo del umbral de 200 ejemplos de calidad) y "
            "nuestro presupuesto exige iterar en minutos con la cuota gratuita de la API. "
            "Como evolucion futura, una vez reunidos los 200 ejemplos de solicitudes normalizadas, PEFT "
            "complementaria a RAG exclusivamente para garantizar el formato JSON estricto de salida."
        ),
        "",
        "## 4. Que necesitarias para ejecutarla",
        (
            "- **Para operar RAG hoy**: Actualmente tenemos 5 documentos cortos indexados en `vectorstore/` "
            "(`doc0` a `doc4`). Para cubrir la operacion completa faltan indexar 15 documentos de politicas "
            "de envios, tarifas vigentes y protocolos de reembolso de `agente_supervision.py` (aproximadamente "
            "10 minutos de preparacion y ejecucion de `indexar_corpus.py`, con costo cercano a $0.0001 USD por consulta).\n"
            "- **Para habilitar PEFT en una fase posterior (formato JSON)**: Hoy tenemos exactamente 12 ejemplos "
            "etiquetados y validados en `dataset_tuning.py` (3 por cada una de las 4 categorias, 0 errores). "
            "Para alcanzar el minimo de 200 ejemplos faltan 188 ejemplos (47 adicionales por categoria); "
            "a 5 minutos por ejemplo bien etiquetado, eso representa 15.67 horas de trabajo humano (casi 2 jornadas "
            "de 8 horas), mas 1.57 horas de segunda revision sobre el 20% aleatorio (38 ejemplos a 2.5 minutos)."
        ),
    ])
    return "\n".join(lineas) + "\n"


if __name__ == "__main__":
    if any(valor is None for valor in respuestas_mi_caso.values()):
        raise SystemExit("Completa las cinco respuestas con True o False antes de continuar.")

    puntos, ganadoras = recomendar_estrategia(respuestas_mi_caso)
    print("=== PASO 1: Resultado sobre nuestro proyecto ===")
    print("Puntajes:", puntos)
    print("Candidatas ganadoras:", ganadoras)

    problema_desc = (
        "Nuestro asistente de operaciones y logistica necesita responder consultas sobre politicas y "
        "tarifas que se actualizan cada mes, y a la vez normalizar solicitudes de clientes en un JSON "
        "estricto de dos claves para decidir aprobacion humana; actualmente solo contamos con 5 documentos "
        "indexados y 12 ejemplos etiquetados en dataset_tuning.py."
    )

    contenido_md = generar_documento_decision(problema_desc, puntos, ganadoras)
    with open("decision_personalizacion.md", "w", encoding="utf-8") as f:
        f.write(contenido_md)
    print("\n=== PASO 2: Archivo 'decision_personalizacion.md' generado ===")

    # Prueba de sensibilidad (Bloque 30-2 pag. 10): cambiar la respuesta mas dudosa
    print("\n=== PRUEBA DE SENSIBILIDAD: si ya tuvieramos >=200 ejemplos (dataset_grande_y_de_calidad=True) ===")
    variante = dict(respuestas_mi_caso)
    variante["dataset_grande_y_de_calidad"] = True
    puntos_v, ganadoras_v = recomendar_estrategia(variante)
    print("Nuevos puntajes:", puntos_v)
    print("Nuevas candidatas:", ganadoras_v)