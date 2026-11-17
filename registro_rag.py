import time
import json
from contextlib import contextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    lineas = []
    for i, doc in enumerate(chunks_recuperados, start=1):
        lineas.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(lineas)


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def registrar_consulta(pregunta, persist_directory="vectorstore/", k=3):
    """Corre una consulta RAG real, midiendo tiempo por etapa y tokens reales
    de la respuesta del modelo."""
    tiempos = {}

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    chat_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    with medir(tiempos, "embed_y_busqueda"):
        vectorstore = Chroma(
            persist_directory=persist_directory, embedding_function=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)

    contexto = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": dict(respuesta.usage_metadata) if respuesta.usage_metadata else None,
    }
    return registro


if __name__ == "__main__":
    # Pruebas exigidas en "Como se prueba" (Bloque 28-3 pag. 6):
    # 1) Al menos 3 preguntas distintas del Bloque 27 con k=3
    preguntas_prueba = [
        "que hace el cliente si una llamada tarda demasiado",
        "como se calcula el costo de una llamada",
        "como decide el agente que herramienta usar",
    ]

    registros = []
    for p in preguntas_prueba:
        reg = registrar_consulta(p, persist_directory="vectorstore/", k=3)
        registros.append(reg)
        print(json.dumps(reg, indent=2, ensure_ascii=False))

    # 2) Misma pregunta con k=6 para comprobar el aumento en input_tokens
    reg_k6 = registrar_consulta(
        preguntas_prueba[0], persist_directory="vectorstore/", k=6
    )
    registros.append(reg_k6)

    # Guardar corridas reales en registros_latencia_costo.jsonl
    with open("registros_latencia_costo.jsonl", "w", encoding="utf-8") as f:
        for reg in registros:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")

    print("\n--- Resumen comparativo (k=3 vs k=6) ---")
    tokens_k3 = registros[0]["tokens"]["input_tokens"] if registros[0]["tokens"] else None
    tokens_k6 = reg_k6["tokens"]["input_tokens"] if reg_k6["tokens"] else None
    print(f"k=3 -> input_tokens={tokens_k3} | total={registros[0]['tiempo_total_ms']} ms")
    print(f"k=6 -> input_tokens={tokens_k6} | total={reg_k6['tiempo_total_ms']} ms")
    print("Registros guardados en registros_latencia_costo.jsonl:", len(registros))