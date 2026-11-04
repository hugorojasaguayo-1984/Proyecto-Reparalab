# Miniaplicación de Consumo de APIs de IA Generativa

Proyecto desarrollado en el marco de la **Especialización en Desarrollo con IA Generativa (Accenture / Skillnest)**.

Esta miniaplicación implementa un cliente modular para interactuar con modelos de lenguaje a través de la API de Google Gemini, incorporando gestión segura de credenciales, arquitectura documentada, banco de prompts con validación de consistencia y pruebas automatizadas.

---

## 🏛️ Guía de Arquitectura

El diseño del sistema sigue una estructura modular desacoplada:

1. **Punto de Entrada (`main.py`)**: Orquesta la ejecución de la miniaplicación desde la raíz del proyecto.
2. **Módulo de Consumo (`src/consumir_gemini.py`)**: Contiene las funciones nucleares de integración:
   - `armar_peticion`: Construye la URL, headers y payload de acuerdo a la API.
   - `enviar_peticion`: Gestiona la llamada HTTP con control de excepciones.
   - `extraer_texto`: Parsea la respuesta JSON estructurada y extrae el contenido generado.
3. **Decisión de Arquitectura y Selección de Modelo**: 
   - Documento de decisión técnica: [`docs/decision-arquitectura.md`](docs/decision-arquitectura.md)
   - Diagrama de arquitectura del flujo de datos: [`docs/diagrama_arquitectura.png`](docs/diagrama_arquitectura.png)
4. **Banco de Prompts y Evaluación de Consistencia (`prompts/`)**:
   - `banco.py`: Definición de prompts de sistema y usuario con salida estructurada JSON.
   - `registro_resultados.json`: Registro empírico de las corridas de prueba.

---

## 🚀 Instalación y Puesta en Marcha

Para clonar y ejecutar este proyecto en un entorno limpio sin intervención manual, sigue estos pasos:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/hugorojasaguayo-1984/Proyecto-Reparalab.git](https://github.com/hugorojasaguayo-1984/Proyecto-Reparalab.git)
cd Proyecto-Reparalab