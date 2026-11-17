from datetime import date
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

K = 3  # cuantos chunks recupera el retriever y cuantos evalua la funcion

# Paso 1: conjunto de evaluacion (entre 8 y 15 preguntas sobre nuestro corpus doc0..doc4)
casos_evaluacion = [
    {"pregunta": "que hace el cliente si una llamada tarda demasiado", "ids_relevantes": {"doc0"}},
    {"pregunta": "cuantos reintentos hace el cliente ante un TimeoutError", "ids_relevantes": {"doc0"}},
    {"pregunta": "que pasa si la clave de api es invalida", "ids_relevantes": {"doc1"}},
    {"pregunta": "los errores de autenticacion se reintentan", "ids_relevantes": {"doc1"}},
    {"pregunta": "como se calcula el costo de una llamada", "ids_relevantes": {"doc2"}},
    {"pregunta": "que campo de tokens se usa para calcular la tarifa", "ids_relevantes": {"doc2"}},
    {"pregunta": "como decide el agente que herramienta usar", "ids_relevantes": {"doc3"}},
    {"pregunta": "en que se basa el agente de la Unidad 2.4 para elegir herramienta", "ids_relevantes": {"doc3"}},
    {"pregunta": "como funcionan las pruebas unitarias del cliente", "ids_relevantes": {"doc4"}},
    {"pregunta": "cuanto tarda en correr la suite de pruebas con mocks", "ids_relevantes": {"doc4"}},
]


def precision_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids recuperados que son relevantes (0.0 si no hay ninguno)."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids relevantes que se recuperaron (None si el caso no tiene ninguno)."""
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores):
    """Promedio que ignora los None y evita dividir por cero."""
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(retriever, casos, k=3):
    """Corre cada caso contra el retriever real y promedia precision y recall."""
    resultados = []
    for caso in casos:
        chunks = retriever.invoke(caso["pregunta"])
        ids_recuperados = [c.id for c in chunks][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({"pregunta": caso["pregunta"], "precision": p, "recall": r})

    precision_promedio = promediar(x["precision"] for x in resultados)
    recall_promedio = promediar(x["recall"] for x in resultados)
    return resultados, precision_promedio, recall_promedio


if __name__ == "__main__":
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(persist_directory="vectorstore/", embedding_function=embeddings)

    print("IDs en vectorstore:", vectorstore.get()["ids"])

    # Corrida 1 con K=3
    retriever_k3 = vectorstore.as_retriever(search_kwargs={"k": K})
    resultados, precision_promedio, recall_promedio = evaluar_recuperacion(
        retriever_k3, casos_evaluacion, k=K
    )

    print("\n--- Corrida 1 (k=3) ---")
    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        print(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}")
    print(f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}")

    # Paso 3: guardar resultados en resultados_evaluacion.txt
    with open("resultados_evaluacion.txt", "w", encoding="utf-8") as archivo:
        archivo.write(f"Fecha: {date.today()}\n")
        archivo.write(f"Configuracion: k={K}, chunk_size=200, chunk_overlap=30\n\n")
        for r in resultados:
            recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
            archivo.write(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}\n")
        archivo.write(
            f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}\n"
        )
    print("\nResultados guardados en resultados_evaluacion.txt")

    # Pruebas exigidas en "Como se prueba" (pag. 7)
    _, p_rep, r_rep = evaluar_recuperacion(retriever_k3, casos_evaluacion, k=K)
    print("Segunda corrida identica a la primera:", (p_rep == precision_promedio and r_rep == recall_promedio))

    retriever_k5 = vectorstore.as_retriever(search_kwargs={"k": 5})
    _, p_k5, r_k5 = evaluar_recuperacion(retriever_k5, casos_evaluacion, k=5)
    print(f"Comparacion k=5 -> precision: {p_k5:.3f}  recall: {r_k5:.3f}")