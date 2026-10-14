"""
Lanzador de escritorio: arranca la API en segundo plano y abre la interfaz
en una ventana nativa (WebView2) con pywebview.
"""
import os
import socket
import sys
import threading
import time
from pathlib import Path

APP_NAME = "Guardias"
HOST = "127.0.0.1"
PREFERRED_PORT = 8765

# Datos persistentes fuera del ejecutable (en --onefile se extrae a una carpeta temporal).
DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / APP_NAME
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Con --noconsole no hay stdout/stderr: se redirigen a un log para no romper uvicorn.
if sys.stdout is None or sys.stderr is None:
    log_file = open(DATA_DIR / "guardias.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or log_file
    sys.stderr = sys.stderr or log_file

# Debe fijarse antes de importar `src`: la configuración de la BD lo lee al importarse.
os.environ.setdefault("DB_DIR", str(DATA_DIR))

from dotenv import load_dotenv  # noqa: E402

# Un .env junto al .exe tiene prioridad sobre el de %APPDATA%\Guardias.
exe_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
load_dotenv(exe_dir / ".env")
load_dotenv(DATA_DIR / ".env")

import uvicorn  # noqa: E402
import webview  # noqa: E402

from src.main import app  # noqa: E402


def _pick_port() -> int:
    """Usa el puerto preferido si está libre; si no, uno cualquiera del sistema."""
    for port in (PREFERRED_PORT, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((HOST, port))
                return sock.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError("No hay puertos libres para arrancar el servidor.")


def main() -> None:
    port = _pick_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host=HOST, port=port, loop="asyncio", http="h11", log_config=None)
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    while not server.started:
        if not thread.is_alive():
            raise RuntimeError("El servidor no pudo arrancar; revisa guardias.log.")
        time.sleep(0.05)

    webview.create_window(
        "Gestor de Guardias",
        f"http://{HOST}:{port}",
        width=1366,
        height=860,
        min_size=(1024, 640),
    )
    webview.start()

    server.should_exit = True
    thread.join(timeout=5)


if __name__ == "__main__":
    main()
