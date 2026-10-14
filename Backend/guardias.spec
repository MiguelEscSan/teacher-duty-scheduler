# -*- mode: python ; coding: utf-8 -*-
# Empaquetado de escritorio. Uso: pyinstaller guardias.spec (o ..\build.ps1)
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).parent
FRONTEND_BUILD = ROOT / "Frontend" / "dist" / "frontend" / "browser"
ICON = Path(SPECPATH) / "assets" / "icon.ico"

if not (FRONTEND_BUILD / "index.html").is_file():
    raise SystemExit(f"No existe el build de Angular en {FRONTEND_BUILD}. Ejecuta antes 'npm run build'.")

# OR-Tools carga librerías nativas que PyInstaller no detecta por sí solo.
ortools_datas, ortools_binaries, ortools_hidden = collect_all("ortools")

a = Analysis(
    ["desktop.py"],
    pathex=[SPECPATH],
    binaries=ortools_binaries,
    datas=[(str(FRONTEND_BUILD), "frontend")] + ortools_datas,
    hiddenimports=ortools_hidden + collect_submodules("uvicorn") + collect_submodules("src"),
    excludes=["pytest", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Guardias",
    icon=str(ICON) if ICON.is_file() else None,
    console=False,
    upx=False,
    runtime_tmpdir=None,
)
