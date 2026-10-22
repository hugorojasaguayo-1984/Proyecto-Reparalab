BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_sentimiento",
        "system_instruction": (
            "Responde únicamente con un JSON con las claves 'sentimiento' "
            "('positivo', 'negativo' o 'neutro') y 'confianza' (0 a 1)."
        ),
        "ejemplo_usuario": "El servicio llegó tarde pero el producto está perfecto.",
        "claves_esperadas": ["sentimiento", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "sentimiento": {"type": "STRING"},
                "confianza": {"type": "NUMBER"}
            },
            "required": ["sentimiento", "confianza"]
        },
    },
    {
        "nombre": "extraer_entidades",
        "system_instruction": (
            "Responde únicamente con un JSON con las claves 'tema' y 'palabras_clave' (lista de cadenas)."
        ),
        "ejemplo_usuario": "Tengo dificultades configurando el entorno virtual en Windows.",
        "claves_esperadas": ["tema", "palabras_clave"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "tema": {"type": "STRING"},
                "palabras_clave": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                }
            },
            "required": ["tema", "palabras_clave"]
        },
    },
    {
        "nombre": "resumen_corto",
        "system_instruction": (
            "Responde únicamente con un JSON con las claves 'resumen' y 'longitud'."
        ),
        "ejemplo_usuario": "La inteligencia artificial generativa permite crear texto, código e imágenes a partir de instrucciones en lenguaje natural.",
        "claves_esperadas": ["resumen", "longitud"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "resumen": {"type": "STRING"},
                "longitud": {"type": "STRING"}
            },
            "required": ["resumen", "longitud"]
        },
    }
]