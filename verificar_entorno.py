import importlib
import os
from dotenv import load_dotenv

load_dotenv()

paquetes = [
    ("google.genai", "google-genai"),
    ("langchain_core", "langchain-core"),
    ("langchain_chroma", "langchain-chroma"),
    ("langgraph", "langgraph"),
    ("dotenv", "python-dotenv"),
    ("pytest", "pytest"),
]

print("=== VERIFICACION DE ENTORNO GATE 2 ===")
todo_ok = True

for modulo, nombre_pip in paquetes:
    try:
        mod = importlib.import_module(modulo)
        version = getattr(mod, "__version__", "instalado")
        print(f"[OK] {nombre_pip}: {version}")
    except ImportError:
        print(f"[FALTA] {nombre_pip} no esta instalado")
        todo_ok = False

if os.getenv("GEMINI_API_KEY"):
    print("[OK] GEMINI_API_KEY detectada")
else:
    print("[FALTA] GEMINI_API_KEY no encontrada en .env")
    todo_ok = False

if os.path.isdir("vectorstore") and os.listdir("vectorstore"):
    print("[OK] Carpeta vectorstore/ persistida y con datos")
else:
    print("[FALTA] Carpeta vectorstore/ vacia o inexistente (ejecuta indexar_corpus.py)")
    todo_ok = False

if todo_ok:
    print("\nEntorno listo para la corrida final")
else:
    print("\nRevisa los puntos marcados con [FALTA] antes de continuar")