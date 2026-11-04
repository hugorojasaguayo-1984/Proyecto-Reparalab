# Informe de Interpretación Cualitativa y Límites del Pipeline de Métricas

**Programa:** Especialización en Desarrollo con IA Generativa (Accenture / Skillnest)  
**Módulo:** Módulo 2 - Construcción de componentes IA  
**Unidad:** U2.2 Pipeline de texto, NLP básico y evaluación inicial  
**Hito:** Bloque 17 - Actividad Core  

---

## 1. Alcance y Definición del Pipeline

El pipeline implementado en `pipeline_texto.py` procesa texto no estructurado mediante dos etapas deterministas:
1. **Limpieza (`limpiar_texto`)**: Normalización a minúsculas y remoción de signos de puntuación mediante expresiones regulares (`re.sub(r'[^\w\s]', '', texto)`).
2. **Tokenización (`tokenizar`)**: Segmentación léxica basada en espacios en blanco.

Sobre los tokens resultantes, se calculan tres métricas formales comparando la respuesta del modelo frente a una referencia humana de verdad fundamental (*ground truth*):
- **Precisión ($P$)**: Proporción de tokens generados por el modelo que coinciden con la referencia ($\text{coincidencias} / |\text{tokens}_{\text{resp}}|$).
- **Cobertura / Recall ($R$)**: Proporción de tokens requeridos por la referencia que fueron generados ($\text{coincidencias} / |\text{tokens}_{\text{ref}}|$).
- **Puntaje $F_1$**: Media armónica formal entre Precisión y Cobertura ($2 \cdot \frac{P \cdot R}{P + R}$).

---

## 2. Modos de Fallo Identificados (Por qué la métrica sola no basta)

El análisis empírico sobre 20 ejecuciones reales demostró tres modos de fallo estructurales propios de métricas basadas exclusivamente en solapamiento léxico de tokens:

### Caso A: Penalización Injusta por Uso de Sinónimos y Parafraseo
- **Fenómeno**: El modelo responde con un hecho 100% verídico y semánticamente equivalente a la referencia, pero utilizando sinónimos o redacción alterna.
- **Impacto**: La métrica $F_1$ cae drásticamente (incluso por debajo del 40%), castigando una respuesta correcta únicamente por no coincidir textualmente con las palabras exactas de la referencia.

### Caso B: Sobreestimación por Verbosidad y Explicación Contextual
- **Fenómeno**: Modelos generativos tienden a responder con frases de cortesía o explicaciones complementarias (e.g., *"La capital de Chile es Santiago, una ciudad ubicada en el valle central..."*).
- **Impacto**: Aunque la cobertura ($R$) sea del 100%, la precisión ($P$) disminuye debido a la longitud de la respuesta, reduciendo artificialmente el valor de $F_1$ a pesar de que la exactitud fáctica es perfecta.

### Caso C: Insensibilidad a la Negación y al Orden Sintáctico
- **Fenómeno**: La inversión de entidades o la adición de una partícula de negación (*"no"*) cambia radicalmente el valor de verdad de una proposición, pero comparte casi la totalidad del vocabulario.
- **Impacto**: Una respuesta fácticamente errónea o contradictoria puede obtener un $F_1 > 85\%$, lo que constituye un falso positivo crítico para la evaluación automatizada.

---

## 3. Auditoría de la Muestra (Top 5 y Bottom 5 según $F_1$)

Se extrajo una muestra estratificada de 10 casos a partir de `resultados_metricas.json` y se evaluó manualmente bajo tres dimensiones: **Exactitud fáctica**, **Completitud** y **Contradicción**:

| ID | Pregunta | $F_1$ Score | Exactitud Fáctica | Completitud | Contradicción | Observación Cualitativa |
|:--:|:---|:---:|:---:|:---:|:---:|:---|
| 1 | ¿Cuál es la capital de Chile? | Alto (>0.85) | Sí | Completa | No | Alta coincidencia directa con la referencia. |
| 2 | ¿Cuál es la capital de Argentina? | Alto (>0.85) | Sí | Completa | No | Respuesta concisa sin ruido léxico. |
| 3 | ¿Cuál es la capital de Perú? | Alto (>0.80) | Sí | Completa | No | Coincidencia de tokens clave. |
| 8 | ¿Cuál es el planeta más cercano al Sol? | Alto (>0.80) | Sí | Completa | No | Identificación unívoca del hecho consultado. |
| 14 | ¿Cuál es el símbolo químico del agua? | Alto (>0.75) | Sí | Completa | No | Precisión alta en término científico conciso. |
| 4 | ¿En qué continente está Francia? | Bajo (<0.50) | Sí | Completa | No | F1 castigado por elaboración detallada del modelo. |
| 6 | ¿Quién escribió Don Quijote...? | Bajo (<0.45) | Sí | Completa | No | Factualmente correcta; F1 penalizado por título extendido. |
| 7 | ¿Cuál es el río más largo del mundo? | Bajo (<0.40) | Sí | Completa | No | F1 bajo debido a contexto geográfico aportado por el modelo. |
| 11 | ¿Cuál es el océano más grande...? | Bajo (<0.40) | Sí | Completa | No | Respuesta correcta pero con vocabulario extendido. |
| 17 | ¿Qué instrumento tiene 88 teclas? | Bajo (<0.35) | Sí | Completa | No | F1 penalizado por explicación sobre teclas blancas y negras. |

El detalle registro por registro se encuentra exportado en `revision_manual.json`.

---

## 4. Recomendaciones Operacionales para Producción

1. **No utilizar métricas puramente léxicas ($F_1$) como criterio único de paso a producción**: Deben complementarse con evaluación semántica (embeddings de similitud coseno) o evaluación LLM-as-a-judge.
2. **Definir umbrales diferenciados según el tipo de consulta**: Consultas factuales cortas admiten monitoreo de tokens directos; consultas analíticas o explicativas requieren validación cualitativa humana periódica.
3. **Control de brevedad en el prompt**: Si se desea maximizar la precisión léxica contra referencias concisas, debe instruirse al modelo en el prompt del sistema a responder en formato estrictamente conciso.