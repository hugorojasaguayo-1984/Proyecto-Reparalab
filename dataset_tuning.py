import json
from collections import Counter
from google.genai import types

# Paso 1: Dataset propio del proyecto (normalizacion de solicitudes de clientes a JSON fijo)
# 12 ejemplos variados repartidos equitativamente en 4 categorias (3 por categoria)
ejemplos_raw = [
    # Categoria: consulta_envio (3)
    (
        "Hola, ¿me puedes decir en que estado va mi paquete AR12345?",
        {"categoria": "consulta_envio", "requiere_aprobacion": False},
    ),
    (
        "Quiero saber si el despacho que salio ayer de bodega ya llego a sucursal.",
        {"categoria": "consulta_envio", "requiere_aprobacion": False},
    ),
    (
        "Necesito revisar el historial completo de movimientos del codigo AR98765.",
        {"categoria": "consulta_envio", "requiere_aprobacion": False},
    ),
    # Categoria: cotizacion (3)
    (
        "¿Cuanto me saldria mandar una caja de 4 kilos a unos 250 kilometros?",
        {"categoria": "cotizacion", "requiere_aprobacion": False},
    ),
    (
        "Necesito estimar el valor del flete para un bulto de 12 kg dentro de la region.",
        {"categoria": "cotizacion", "requiere_aprobacion": False},
    ),
    (
        "Si envio dos paquetes que suman 7.5 kg a 600 km, ¿cual seria la tarifa aproximada?",
        {"categoria": "cotizacion", "requiere_aprobacion": False},
    ),
    # Categoria: reembolso (3)
    (
        "El pedido AR12345 llego totalmente quebrado, exijo la devolucion de los $15000.",
        {"categoria": "reembolso", "requiere_aprobacion": True},
    ),
    (
        "Me cobraron doble el envio del pedido PED789, por favor reembolsen $1200 a mi cuenta.",
        {"categoria": "reembolso", "requiere_aprobacion": True},
    ),
    (
        "Cancele el despacho antes de que saliera y necesito que me devuelvan los $8500 pagados.",
        {"categoria": "reembolso", "requiere_aprobacion": True},
    ),
    # Categoria: reclamo (3)
    (
        "Llevo cinco dias esperando la entrega y nadie me da una explicacion clara.",
        {"categoria": "reclamo", "requiere_aprobacion": False},
    ),
    (
        "El repartidor dejo el paquete bajo la lluvia en la reja sin tocar el timbre.",
        {"categoria": "reclamo", "requiere_aprobacion": False},
    ),
    (
        "Me atendieron muy mal en la sucursal central cuando fui a retirar mi encomienda.",
        {"categoria": "reclamo", "requiere_aprobacion": False},
    ),
]

examples = [
    types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
    for texto, salida in ejemplos_raw
]


# Paso 2: Revisar el balance entre categorias
def chequear_balance(ejemplos: list[tuple[str, dict]], clave: str) -> Counter:
    """Cuenta cuantos ejemplos hay por cada valor de la clave indicada."""
    categorias = Counter(salida[clave] for _, salida in ejemplos)
    return categorias


# Paso 3: Validar formato JSON, claves esperadas, vacios y duplicados
def validar_dataset(
    examples: list[types.TuningExample], claves_esperadas: tuple[str, ...]
) -> list[str]:
    """Valida que cada ejemplo tenga texto, output JSON valido y todas las claves esperadas."""
    problemas = []
    vistos = set()
    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)
        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas


if __name__ == "__main__":
    print("=== PASO 1: Construccion del dataset ===")
    print(f"{len(examples)} ejemplos construidos")
    print("Primer ejemplo:", examples[0])

    print("\n=== PASO 2: Balance entre categorias ===")
    balance = chequear_balance(ejemplos_raw, "categoria")
    for categoria, cuenta in balance.most_common():
        print(f"  {categoria}: {cuenta}")
    maximo = max(balance.values())
    minimo = min(balance.values())
    print(f"Razon max/min: {maximo / minimo:.1f}x")

    print("\n=== PASO 3: Validacion del dataset limpio ===")
    claves = ("categoria", "requiere_aprobacion")
    problemas = validar_dataset(examples, claves_esperadas=claves)
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for p in problemas:
        print(" -", p)

    print("\n=== PRUEBA DE CONTROL: Validacion sobre dataset roto a proposito ===")
    examples_rotos = examples + [
        types.TuningExample(text_input="", output='{"categoria": "reclamo"}'),
        types.TuningExample(text_input=ejemplos_raw[0][0], output="no es json"),
    ]
    problemas_rotos = validar_dataset(examples_rotos, claves_esperadas=claves)
    print(f"{len(examples_rotos)} ejemplos, {len(problemas_rotos)} problemas encontrados")
    for p in problemas_rotos:
        print(" -", p)