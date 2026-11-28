# Servicio IA Modular con RAG, Observabilidad y Gobernanza — Gate 2

**Autor:** Hugo Hernán Rojas Aguayo  
**Programa:** Especialización en Desarrollo con IA Generativa (Accenture / Skillnest)  
**Repositorio:** https://github.com/hugorojasaguayo-1984/Proyecto-Reparalab

Este repositorio implementa un servicio modular de IA Generativa de extremo a extremo que integra:
- **RAG persistido localmente** con Chroma (`vectorstore/`) y embeddings reales (`models/gemini-embedding-001`).
- **Recuperación semántica evaluada** (`precision@k`, `recall@k`, determinismo) y generación con **citas vinculantes** (`gemini-3.5-flash-lite`).
- **Telemetría de latencia y costo** en formato JSONL (`registros_latencia_costo.jsonl`).
- **Estrategia de personalización fundamentada** (RAG vs. PEFT vs. Full fine-tuning).
- **Observabilidad estructurada en JSON** con aislamiento de `trace_id` vía `contextvars` en `logs/gate2.log` y **cero exposición de PII o texto crudo**.
- **Seguridad y gobernanza**: filtro anti-inyección de prompt compatible con objetos `Document` de LangChain, rama segura de contexto vacío sin llamada al LLM, versionado de prompts por SHA-256 con `diff`, matriz de riesgos propia (6 filas) y supervisión humana real (**Human-in-the-Loop**) con LangGraph (`interrupt()` + `Command(resume=...)`).

## 1. Requisitos previos (Entorno limpio)

- **Python:** 3.11 o superior.
- **Git:** instalado y disponible en terminal.
- **API Key de Google Gemini:** variable `GEMINI_API_KEY` con acceso a `models/gemini-embedding-001` y `gemini-3.5-flash-lite`.

## 2. Guía paso a paso para clonar y ejecutar desde cero

Sigue estos pasos en orden exacto para reproducir el proyecto en un entorno completamente limpio.

### Paso 1 — Clonar el repositorio
```bash
git clone [https://github.com/hugorojasaguayo-1984/Proyecto-Reparalab.git](https://github.com/hugorojasaguayo-1984/Proyecto-Reparalab.git)
cd Proyecto-Reparalab
```

### Paso 2 — Crear y activar el entorno virtual

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(Si PowerShell bloquea la activación por política de ejecución, corre antes: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y repite `.\venv\Scripts\Activate.ps1`).*

**En macOS / Linux (Bash/Zsh):**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3 — Instalar dependencias exactas
```bash
pip install -r requirements.txt
```

### Paso 4 — Configurar la API Key (`.env`)
El archivo `.env` está protegido en `.gitignore` y **no** se sube al repositorio. Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```env
GEMINI_API_KEY=tu_clave_real_de_gemini_aqui
```

### Paso 5 — Indexar el corpus y persistir `vectorstore/`
La carpeta `vectorstore/` se excluye del control de versiones para evitar binarios locales y se construye una sola vez en disco ejecutando:

```bash
python indexar_corpus.py
```
**Resultado esperado:** `Reindexados 5 chunks en vectorstore/, ahora con metadata e ids`  
*(Una vez creado `vectorstore/`, `ensayo_gate2.py` carga el índice directamente desde disco sin reconstruirlo en cada consulta).*

### Paso 6 — Verificar que el entorno está listo
```bash
python verificar_entorno.py
```
**Resultado esperado:** Todos los paquetes marcados con `[OK]`, `GEMINI_API_KEY detectada`, `Carpeta vectorstore/ persistida y con datos` y la línea final:
`Entorno listo para la corrida final`

### Paso 7 — Ejecutar el ensayo funcional integrado de punta a punta
```bash
python ensayo_gate2.py
```
**Qué ejecuta y verifica en vivo:**
1. Consulta normal sobre `vectorstore/` persistido, devolviendo respuesta con cita explícita de fuente (`doc0.md`..`doc4.md`).
2. Consulta con dato personal simulado (`ana.perez@correo.com`) para demostrar que las trazas en `logs/gate2.log` solo guardan largo (`pregunta_len`) y huella SHA-256 (`pregunta_hash`), jamás PII ni texto crudo.
3. Documento con ataque de inyección de prompt: el filtro lo descarta y activa la rama segura `RESPUESTA_SIN_CONTEXTO` sin llamar al LLM.
4. Supervisión humana real con LangGraph: pausa en `__interrupt__` (`True`) sobre la huella de prompt `86dc01a19526` y reanuda tras `Command(resume=True)`.

### Paso 8 — Ejecutar las pruebas automáticas del Gate 2 (4 Criterios Innegociables)
```bash
python -m pytest test_gate2.py -v
```
**Resultado esperado:** `5 passed` (0 fallos).

*(Opcional: para correr toda la suite histórica del repositorio, ejecutar `python -m pytest -v`).*

### Paso 9 — Auditoría manual de privacidad en logs (Criterio Innegociable #3)

**En Windows (PowerShell):**
```powershell
findstr /s /i ana.perez logs\*
```

**En macOS / Linux:**
```bash
grep -ri "ana.perez" logs/
```
**Resultado esperado:** **Salida completamente vacía** (0 coincidencias).

## 3. Verificación rápida de los 4 Criterios Innegociables

| # | Criterio Innegociable | Implementación | Cómo verificarlo | Resultado esperado |
| :-: | :--- | :--- | :--- | :--- |
| **1** | El pipeline indexa/carga, recupera y responde sin excepciones no manejadas | `indexar_corpus.py` + `ensayo_gate2.py` (`cargar_indice`, `ejecutar_servicio`) | `python -m pytest test_gate2.py -k test_1 -v` | `PASSED` |
| **2** | Toda respuesta cita explícitamente la fuente que la respalda | `ensayo_gate2.py` (`formatear_contexto_seguro`, `PROMPT_RAG_V2`) | `python -m pytest test_gate2.py -k test_2 -v` | `PASSED` (cita `doc*.md`) |
| **3** | Ningún log contiene PII ni texto crudo de prompts/preguntas | `ensayo_gate2.py` (`JsonFormatter`, `logs/gate2.log`) | `python -m pytest test_gate2.py -k test_3 -v` y `findstr /s /i ana.perez logs\*` | `PASSED` y 0 coincidencias |
| **4** | Al menos un punto de supervisión humana (HITL) pausa y reanuda realmente | `ensayo_gate2.py` (`crear_supervision`, `interrupt()`, `Command(resume=...)`) | `python -m pytest test_gate2.py -k test_4 -v` | `PASSED` (prueba aprobación y rechazo) |

## 4. Cobertura de las 6 Dimensiones de la Rúbrica (100%)

| Dimensión (Peso) | Evidencia y archivos en el repositorio | Comando de verificación |
| :--- | :--- | :--- |
| **1. Pipeline RAG funcional (25%)** | `indexar_corpus.py`, `vectorstore/` persistido (sin reconstruir por corrida), `ensayo_gate2.py` | `python ensayo_gate2.py` |
| **2. Recuperación y citas (15%)** | `recuperacion.py`, `evaluacion_recuperacion.py`, `resultados_evaluacion.txt` (`precision@3 = 0.333`, `recall@3 = 1.000`, determinista = `True`) | `python evaluacion_recuperacion.py` |
| **3. Costo, latencia y operación (10%)** | `registro_rag.py`, `registros_latencia_costo.jsonl` (`k=3`: 149 tokens / 9610.84 ms vs `k=6`: 202 tokens / 12377.27 ms) | `python registro_rag.py` |
| **4. Personalización justificada (15%)** | `dataset_tuning.py` (12 ejemplos balanceados), `decision.py`, `decision_personalizacion.md` y Sección 6 de este README | `python decision.py` |
| **5. Observabilidad y trazabilidad (15%)** | `logging_rag.py`, `ensayo_gate2.py` y carpeta `logs/gate2.log` con eventos JSON, `trace_id` aislado y consumo de tokens | `python ensayo_gate2.py` |
| **6. Seguridad, versionado y gobernanza (20%)** | Filtro anti-inyección (`logging_rag.py` + `ensayo_gate2.py`), `registro_prompts.py` (SHA-256 + `diff`), `grafo_supervision.py`, `matriz_riesgos.py` y Sección 7 de este README | `python -m pytest test_gate2.py -v` |

## 5. Estructura del repositorio

```text
Proyecto-Reparalab/
├── .gitignore                      # Protege .env, venv/, __pycache__/ y vectorstore/
├── README.md                       # Documentación completa, reproducción, estrategia y matriz de riesgos
├── requirements.txt                # Dependencias congeladas del entorno virtual
├── verificar_entorno.py            # Validador previo de librerías, GEMINI_API_KEY y vectorstore/
├── ensayo_gate2.py                 # Orquestador integrado Gate 2 (RAG + Filtro + Logs JSON + HITL)
├── test_gate2.py                   # 5 pruebas automáticas (4 innegociables + defensa contexto vacío)
├── logs/
│   └── gate2.log                   # Trazas JSON auditables con trace_id y consumo (sin PII)
├── indexar_corpus.py               # Indexación y persistencia de chunks con metadata e ids en Chroma
├── recuperacion.py                 # Recuperación semántica y armado de prompt con citas
├── evaluacion_recuperacion.py      # Evaluación cuantitativa precision@k y recall@k
├── resultados_evaluacion.txt       # Reporte de métricas de recuperación
├── registro_rag.py                 # Medición de latencia y tokens comparando k=3 vs k=6
├── registros_latencia_costo.jsonl  # Telemetría operativa real en formato JSONL
├── dataset_tuning.py               # Dataset balanceado (12 ejemplos, 4 categorías) y validador
├── decision.py                     # Motor de decisión reproducible (RAG vs PEFT vs Fine-tuning)
├── decision_personalizacion.md     # Documento fundamentado de estrategia de personalización
├── logging_rag.py                  # Logging estructurado JSON, contextvars y filtro anti-inyección
├── registro_prompts.py             # Versionado de prompts con huella SHA-256 y unified_diff
├── grafo_supervision.py            # Grafo LangGraph HITL (aprobación y rechazo en hilos separados)
├── matriz_riesgos.py               # Cálculo de severidad, límites y puntos de supervisión
└── agente_*.py / test_*.py         # Módulos y suite de pruebas unitarias de Unidades 2.1–2.4
```

## 6. Estrategia de Personalización (Bloques 29 y 30)

El análisis detallado está en `decision_personalizacion.md` y se reproduce con `python decision.py`.

| Estrategia | Puntaje obtenido | Decisión |
| :--- | :---: | :--- |
| **RAG (Retrieval-Augmented Generation)** | **5 pts** | **Estrategia seleccionada** |
| PEFT / LoRA | 3 pts | Opción futura si el dataset validado supera los 200 ejemplos |
| Full fine-tuning | 1 pt | Descartada por alto costo, infraestructura y conocimiento cambiante |

**Fundamento técnico:** El proyecto opera sobre documentación viva que requiere actualización frecuente y trazabilidad obligatoria por cita (`doc0.md`..`doc4.md`). Actualmente dispone de 12 ejemplos etiquetados y balanceados (`consulta_envio`, `cotizacion`, `reembolso`, `reclamo` en `dataset_tuning.py`), volumen insuficiente para justificar fine-tuning. RAG entrega precisión verificable (`recall@3 = 1.000`) y control de costo (`k=3` usa 149 tokens de entrada frente a 202 con `k=6`).

## 7. Matriz de Riesgos de IA Generativa (Bloque 32)

| Riesgo | Probabilidad (1-5) | Impacto (1-5) | Severidad | Mitigación implementada | Punto de supervisión humana (HITL) |
| :--- | :---: | :---: | :---: | :--- | :--- |
| Inyección de prompt indirecta vía documento o comentario recuperado en Chroma | 4 | 4 | **CRÍTICO (16)** | Filtro regex `detectar_inyeccion` + delimitadores `<contexto>` + rama segura `RESPUESTA_SIN_CONTEXTO` en `ensayo_gate2.py` y `logging_rag.py` | Revisión humana antes de responder cuando el filtro descarta documentos |
| Ejecución autónoma de reembolso monetario sin autorización humana | 3 | 5 | **CRÍTICO (15)** | Validación Pydantic y bloqueo `esperar_aprobacion()` en `agente_supervision.py` (Bloque 23) | Confirmación explícita del supervisor humano antes de ejecutar `generar_reembolso` |
| Filtración de datos personales (PII) de clientes en logs de producción sin redactar | 3 | 4 | **ALTO (12)** | Logging estructurado JSON registrando `pregunta_len` y `pregunta_hash` (SHA-256) en vez de texto crudo en `ensayo_gate2.py` | Aprobación humana para acceso a logs y auditoría periódica de `logs/gate2.log` |
| Despliegue a producción de una nueva versión de prompt sin revisión ni diff | 3 | 3 | **ALTO (9)** | Registro de huellas SHA-256 (`86dc01a19526`) y `diff_prompts` en `registro_prompts.py` | `interrupt()` de LangGraph con `Command(resume=...)` en `ensayo_gate2.py` y `grafo_supervision.py` |
| Degradación silenciosa en recuperación RAG por cambio de embeddings o chunks obsoletos | 2 | 4 | **MEDIO (8)** | Evaluación periódica `precision@k`/`recall@k` en `evaluacion_recuperacion.py` e `ids` explícitos en `indexar_corpus.py` | Revisión al actualizar el corpus o el modelo de embeddings |
| Inconsistencia menor de formato JSON en consultas informativas de bajo impacto | 1 | 2 | **BAJO (2)** | Dataset balanceado de 12 ejemplos en `dataset_tuning.py` y estrategia RAG documentada en `decision_personalizacion.md` | Revisión por muestreo en pruebas de regresión |

## 8. Registro del Ensayo Funcional (Gate 2)

- **Fecha de verificación:** 28/11/2026
- **Modelo generativo / embeddings:** `gemini-3.5-flash-lite` / `models/gemini-embedding-001`
- **Versión de prompt activa (SHA-256):** `86dc01a19526`
- **Pruebas automáticas (`python -m pytest test_gate2.py -v`):** `5 passed in 10.81s`
- **Auditoría de privacidad (`findstr /s /i ana.perez logs\*`):** 0 coincidencias en `logs/gate2.log`

## 9. Solución de problemas frecuentes (Troubleshooting)

- **`Falta GEMINI_API_KEY en el entorno (.env)`:** Verifica que creaste el archivo `.env` en la raíz del proyecto con `GEMINI_API_KEY=tu_clave`.
- **`No existe 'vectorstore/'` o `'vectorstore/' esta vacio`:** Ejecuta `python indexar_corpus.py` una vez antes de correr `ensayo_gate2.py` o `pytest`.
- **Error de política de ejecución en PowerShell al activar `venv`:** Ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a correr `.\venv\Scripts\Activate.ps1`.