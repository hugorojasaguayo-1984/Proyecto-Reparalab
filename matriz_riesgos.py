def puntaje_riesgo(probabilidad: int, impacto: int) -> int:
    return probabilidad * impacto


def categoria_riesgo(puntaje: int) -> str:
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad: int, impacto: int) -> bool:
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto),
        (probabilidad - 1, impacto),
        (probabilidad, impacto + 1),
        (probabilidad, impacto - 1),
    ]
    for p2, i2 in vecinos:
        if not (1 <= p2 <= 5 and 1 <= i2 <= 5):
            continue
        if categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False


# Matriz de riesgos concretos de nuestro proyecto (minimo 5 filas)
mis_riesgos = [
    {
        "riesgo": "Inyeccion de prompt indirecta via documento o comentario recuperado en Chroma",
        "probabilidad": 4,
        "impacto": 4,
        "mitigacion": "Filtro de patrones sospechosos + delimitadores <contexto> en logging_rag.py (Bloque 31)",
        "punto_supervision": "Revision humana antes de responder cuando el filtro marca un documento",
    },
    {
        "riesgo": "Ejecucion autonoma de reembolso monetario sin autorizacion humana",
        "probabilidad": 3,
        "impacto": 5,
        "mitigacion": "Validacion Pydantic y bloqueo con esperar_aprobacion() en agente_supervision.py (Bloque 23)",
        "punto_supervision": "Confirmacion explicita del supervisor humano antes de ejecutar generar_reembolso",
    },
    {
        "riesgo": "Filtracion de datos personales (PII) de clientes en logs de produccion sin redactar",
        "probabilidad": 3,
        "impacto": 4,
        "mitigacion": "Logging estructurado JSON registrando pregunta_len y huella SHA-256 en vez de texto (Bloque 31)",
        "punto_supervision": "Aprobacion humana para acceso a logs y auditoria semanal de trazas_agente.jsonl",
    },
    {
        "riesgo": "Despliegue a produccion de una nueva version de prompt sin revision ni diff",
        "probabilidad": 3,
        "impacto": 3,
        "mitigacion": "Registro de huellas y diff_prompts en registro_prompts.py (Bloque 32)",
        "punto_supervision": "Interrupt de LangGraph con Command(resume=...) en grafo_supervision.py",
    },
    {
        "riesgo": "Degradacion silenciosa en recuperacion RAG por cambio de modelo de embeddings o chunks desactualizados",
        "probabilidad": 2,
        "impacto": 4,
        "mitigacion": "Evaluacion periodica precision@k/recall@k en evaluacion_recuperacion.py e ids explicitos (Bloques 26 y 27)",
        "punto_supervision": "No aplica (revision tecnica periodica sin pausa en linea)",
    },
    {
        "riesgo": "Inconsistencia menor de formato JSON en consultas informativas de bajo impacto",
        "probabilidad": 1,
        "impacto": 2,
        "mitigacion": "Dataset balanceado de 12 ejemplos en dataset_tuning.py y estrategia RAG+PEFT (Bloques 29 y 30)",
        "punto_supervision": "No aplica (riesgo bajo)",
    },
]

if __name__ == "__main__":
    for r in mis_riesgos:
        r["puntaje"] = puntaje_riesgo(r["probabilidad"], r["impacto"])
        r["categoria"] = categoria_riesgo(r["puntaje"])
        r["al_limite"] = esta_en_el_limite(r["probabilidad"], r["impacto"])

    print("=== MATRIZ DE RIESGOS DEL PROYECTO (ORDENADA POR SEVERIDAD) ===")
    for r in sorted(mis_riesgos, key=lambda x: -x["puntaje"]):
        marca = " [AL LIMITE]" if r["al_limite"] else ""
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']}{marca}")
        print(f"   Mitigacion: {r['mitigacion']}")
        if r["categoria"] in ("CRITICO", "ALTO"):
            print(f"   Punto de supervision: {r['punto_supervision']}")

    print("\n=== FILAS AL LIMITE PARA REVISION CON OTRA PERSONA ===")
    for r in mis_riesgos:
        if r["al_limite"]:
            print(" - Revisar con otra persona:", r["riesgo"])