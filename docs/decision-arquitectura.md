# Decisión de arquitectura: elección de modelo

## Modelo elegido
**Google Gemini 1.5 Flash** (`gemini-3.5-flash` en la API v1beta de Google Generative Language).

Este modelo fue seleccionado como el motor de lenguaje principal para la miniaplicación de **Reparalab**.

## Diagrama de arquitectura
El flujo completo de ejecución, el aislamiento de credenciales en `.env`, el manejo modular de excepciones y el punto de cálculo de costos en vivo se encuentran representados en el siguiente diagrama:

[diagrama_arquitectura.png]

*El archivo en alta resolución se encuentra versionado en este repositorio en `docs/diagrama_arquitectura.png`.*

## Comparación de candidatos

Para sustentar la elección con métricas concretas y reproducibles, se contrastaron dos variantes de la misma familia respaldadas por los precios oficiales de Google Cloud y las mediciones de latencia promedio obtenidas en el entorno de desarrollo:

| Criterio | Modelo A: Gemini 1.5 Flash (Seleccionado) | Modelo B: Gemini 1.5 Pro (Descartado) |
| :--- | :--- | :--- |
| **Costo por 1.000 tokens de entrada** | 0.000075 USD ($0.075 / 1M) | 0.001250 USD ($1.25 / 1M) |
| **Costo por 1.000 tokens de salida** | 0.000300 USD ($0.30 / 1M) | 0.005000 USD ($5.00 / 1M) |
| **Latencia promedio observada** | **3.01 segundos** (medida real: 2.99s, 3.19s, 2.89s, 2.97s) | ~6.80 segundos (estimada de referencia) |
| **Calidad de respuesta para el caso** | Excelente: respuestas claras, precisas y concisas para asistencia y clasificación técnica. | Muy alta: razonamiento analítico profundo y análisis exhaustivo de documentos masivos. |
| **Fecha de medición** | Octubre 2026 | Octubre 2026 |

## Justificación
Para la miniaplicación de **Reparalab**, la prioridad de diseño es brindar soporte interactivo ágil y eficiente sin incurrir en sobrecostos operativos:

1. **Costo a escala:** Gemini 1.5 Flash es **16 veces más económico** que Gemini 1.5 Pro. Para un volumen proyectado de 50.000 consultas mensuales, operar con Flash representa un costo aproximado de **$3.60 USD**, frente a más de **$60.00 USD** mensuales que exigiría Pro para resolver exactamente la misma tarea.
2. **Latencia y experiencia de usuario:** Los 3.01 segundos de latencia promedio observados permiten una interacción fluida en un asistente transaccional, mientras que los tiempos superiores de Pro (>6 segundos) generan fricción y abandono por parte del usuario.
3. **Calidad adecuada:** Las capacidades de Flash satisfacen con creces la generación de respuestas breves y la posterior estructuración en JSON requerida en los siguientes bloques.

## Alternativa descartada y por qué
Se descartó formalmente **Gemini 1.5 Pro**.

Aunque es un modelo con capacidades sobresalientes en razonamiento científico complejo y ventanas de contexto de hasta 2 millones de tokens, para las necesidades de Reparalab representa una **sobredimensión innecesaria**. Su costo 16 veces más alto y su latencia significativamente mayor no aportan un valor diferencial que justifique su adopción en esta etapa.