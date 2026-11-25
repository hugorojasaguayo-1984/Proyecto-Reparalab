# Decision de personalizacion: asistente de operaciones y logistica

## 1. El problema
Nuestro asistente de operaciones y logistica necesita responder consultas sobre politicas y tarifas que se actualizan cada mes, y a la vez normalizar solicitudes de clientes en un JSON estricto de dos claves para decidir aprobacion humana; actualmente solo contamos con 5 documentos indexados y 12 ejemplos etiquetados en dataset_tuning.py.

## 2. Resultado del metodo de decision
- RAG: 5 puntos
- PEFT: 3 puntos
- Fine-tuning completo: 1 puntos

## 3. Tecnica elegida y por que
Elijo **RAG** como tecnica principal inmediata (ganadora clara con 5 puntos frente a 3 de PEFT y 1 de Fine-tuning completo). Las tarifas, estados de pedidos y reglas operativas cambian periodicamente, por lo que reindexar documentos en Chroma toma segundos y no requiere reentrenar ni pagar trabajos de tuning. Descarto Fine-tuning completo y PEFT en esta etapa porque solo contamos con 12 ejemplos etiquetados (muy por debajo del umbral de 200 ejemplos de calidad) y nuestro presupuesto exige iterar en minutos con la cuota gratuita de la API. Como evolucion futura, una vez reunidos los 200 ejemplos de solicitudes normalizadas, PEFT complementaria a RAG exclusivamente para garantizar el formato JSON estricto de salida.

## 4. Que necesitarias para ejecutarla
- **Para operar RAG hoy**: Actualmente tenemos 5 documentos cortos indexados en `vectorstore/` (`doc0` a `doc4`). Para cubrir la operacion completa faltan indexar 15 documentos de politicas de envios, tarifas vigentes y protocolos de reembolso de `agente_supervision.py` (aproximadamente 10 minutos de preparacion y ejecucion de `indexar_corpus.py`, con costo cercano a $0.0001 USD por consulta).
- **Para habilitar PEFT en una fase posterior (formato JSON)**: Hoy tenemos exactamente 12 ejemplos etiquetados y validados en `dataset_tuning.py` (3 por cada una de las 4 categorias, 0 errores). Para alcanzar el minimo de 200 ejemplos faltan 188 ejemplos (47 adicionales por categoria); a 5 minutos por ejemplo bien etiquetado, eso representa 15.67 horas de trabajo humano (casi 2 jornadas de 8 horas), mas 1.57 horas de segunda revision sobre el 20% aleatorio (38 ejemplos a 2.5 minutos).
