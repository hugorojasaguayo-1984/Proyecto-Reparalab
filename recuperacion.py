from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
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
    """Arma un bloque de contexto numerado para el prompt, y un mapa
    numero -> fuente para reconstruir la cita despues."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n\n".join(lineas)
    return contexto, citas


def construir_prompt(pregunta, persist_directory="vectorstore/", k=3):
    """Recupera los k chunks mas relevantes para la pregunta y arma
    el prompt dinamico con contexto numerado, listo para pasarle al modelo."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    chunks_recuperados = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks_recuperados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return prompt, citas


if __name__ == "__main__":
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)

    # Prueba 1: Primera pregunta sobre el corpus
    print("=== PRUEBA 1: Pregunta sobre errores de red ===")
    p1 = "¿Qué hace el cliente si hay un TimeoutError?"
    prompt_1, citas_1 = construir_prompt(p1, persist_directory="vectorstore/", k=3)
    print(prompt_1)
    print("Citas:", citas_1)
    resp_1 = modelo.invoke(prompt_1)
    print("Respuesta modelo:", resp_1.content)

    # Prueba 2: Segunda pregunta distinta sobre el corpus (el orden de chunks debe cambiar)
    print("\n=== PRUEBA 2: Pregunta sobre el agente ===")
    p2 = "¿Cómo decide el agente qué herramienta usar?"
    prompt_2, citas_2 = construir_prompt(p2, persist_directory="vectorstore/", k=3)
    print(prompt_2)
    print("Citas:", citas_2)
    resp_2 = modelo.invoke(prompt_2)
    print("Respuesta modelo:", resp_2.content)

    # Prueba 3: Pregunta fuera del corpus (debe admitir que no tiene información)
    print("\n=== PRUEBA 3: Pregunta fuera del corpus ===")
    p3 = "¿Cuál es la capital de Francia?"
    prompt_3, citas_3 = construir_prompt(p3, persist_directory="vectorstore/", k=3)
    resp_3 = modelo.invoke(prompt_3)
    print("Respuesta modelo:", resp_3.content)