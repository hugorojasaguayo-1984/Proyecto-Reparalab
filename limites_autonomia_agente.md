# Límites de Autonomía y Supervisión Humana: Agente de Operaciones y Logística

## 1. Catálogo de Herramientas y Nivel de Riesgo

Cada herramienta integrada en el agente ha sido clasificada según su impacto operacional y financiero:

- **`consultar_estado_envio_con_historial`**: **Riesgo Bajo (Solo Lectura)**.
  - *Justificación*: Consulta únicamente el estado y el historial de pedidos en la base de datos simulada. No altera registros ni realiza escrituras. Si el agente comete un error en los parámetros, el peor escenario es una respuesta informativa incorrecta o vacía, sin impacto en el negocio ni en los clientes.
- **`calcular_costo_envio`**: **Riesgo Bajo (Solo Cálculo)**.
  - *Justificación*: Ejecuta una fórmula aritmética en memoria para estimar tarifas según peso y distancia. No modifica bases de datos ni compromete fondos económicos.
- **`generar_reembolso`**: **Riesgo Alto (Escritura Irreversible con Impacto Económico)**.
  - *Justificación*: Emite transferencias y movimientos de dinero hacia clientes. Un error en la invocación o en el monto representaría pérdidas financieras irreversibles directas para la empresa. Por diseño, el agente jamás puede ejecutarla de manera autónoma; requiere supervisión humana obligatoria.

---

## 2. Herramientas que Requieren Aprobación Humana (Human-in-the-Loop)

- **`generar_reembolso`**:
  - *Motivo de la aprobación*: Mitigar el riesgo de desembolsos monetarios indebidos causados por alucinaciones del modelo, ambigüedades en la conversación o intentos de manipulación de instrucciones (prompt injection).
  - *Mecanismo implementado*: La herramienta intercepta la ejecución mediante la función `esperar_aprobacion()`, presentando al supervisor humano los argumentos exactos (`numero_pedido` y `monto`). Si el supervisor no aprueba explícitamente respondiendo `'s'`, la acción financiera se aborta de inmediato y el rechazo queda auditado en `registro_aprobaciones`.

---

## 3. Revisión de Trazas de Decisión

- **Persistencia**: Cada ciclo de razonamiento y acción del agente se almacena en formato estructurado en `trazas_agente.jsonl` mediante `registrar_traza()`. Se registran marca de tiempo UTC, ID de sesión, consulta original, llamadas intermedias a herramientas (con argumentos y observaciones) y la respuesta final devuelta.
- **Frecuencia de auditoría**:
  - *Revisiones periódicas*: Semanalmente se audita una muestra aleatoria de sesiones informativas.
  - *Auditoría obligatoria 100%*: Cualquier interacción que involucre herramientas de riesgo alto (`generar_reembolso`) o presente quejas se audita de forma continua.
- **Patrones sospechosos que se buscan**:
  1. *Llamadas consecutivas repetidas*: La misma herramienta ejecutada en bucle con argumentos idénticos o similares (detectable con `marcar_repeticiones_sospechosas`), señal de estancamiento del agente.
  2. *Ejecución sin aprobación*: Cualquier registro de reembolso en la traza que carezca de su correspondiente entrada aprobada en la auditoría humana.
  3. *Inconsistencia de observación vs. respuesta*: Respuestas finales que aseguren hechos no presentes en ninguna observación devuelta por las herramientas (alucinación de datos).

---

## 4. Plan de Acción ante Comportamiento Inesperado

Si durante la auditoría o en producción el agente presenta comportamiento anómalo o degradación en sus decisiones, se procede en el siguiente orden estricto:

1. **Desactivación selectiva de la herramienta comprometida**: Remover temporalmente la herramienta de la lista `herramientas` en el ejecutor, degradando el agente a un modo meramente informativo.
2. **Revisión y ajuste del System Prompt y descripciones**: Clarificar las instrucciones del sistema, reduciendo la ambigüedad en el `args_schema` de las herramientas o reforzando restricciones de contexto.
3. **Restricción de parámetros en Pydantic**: Incorporar validaciones estrictas (por ejemplo, topes máximos en montos de reembolso o validación regex en formatos de pedido).
4. **Pruebas de regresión automatizadas**: Ejecutar el conjunto de pruebas unitarias (`pytest`) para validar que las correcciones resuelvan el fallo sin afectar los flujos existentes antes del re-despliegue.