from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def proponer(estado: EstadoDespliegue):
    return {}


def supervisar(estado: EstadoDespliegue):
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
    })
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("version", estado["huella_nueva"], "activada")
    else:
        print("version", estado["huella_nueva"], "rechazada, se mantiene la anterior")
    return {}


grafo = StateGraph(EstadoDespliegue)
grafo.add_node("proponer", proponer)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)
grafo.add_edge(START, "proponer")
grafo.add_edge("proponer", "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    # Huella real obtenida en registro_prompts.py (Paso 1)
    huella = "376262961124"

    # Camino 1: Aprobacion humana (thread_id unico)
    print("=== CAMINO 1: APROBACION HUMANA ===")
    config_1 = {"configurable": {"thread_id": "mi-despliegue-1"}}
    res_1 = app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config_1)
    assert "__interrupt__" in res_1, "El grafo debio pausar en el interrupt"
    print("1) tras invocar (pausado):", res_1)
    print("2) pendiente:", app_despliegue.get_state(config_1).interrupts[0].value)

    res_1_final = app_despliegue.invoke(Command(resume=True), config=config_1)
    print("3) tras aprobar:", res_1_final)

    # Camino 2: Rechazo humano (nuevo thread_id para no reusar el hilo ya resuelto)
    print("\n=== CAMINO 2: RECHAZO HUMANO ===")
    config_2 = {"configurable": {"thread_id": "mi-despliegue-2"}}
    app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config_2)
    res_2_final = app_despliegue.invoke(Command(resume=False), config=config_2)
    print("4) tras rechazar:", res_2_final)