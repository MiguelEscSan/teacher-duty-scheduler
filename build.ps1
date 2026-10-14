# Genera Backend\dist\Guardias.exe: compila Angular y empaqueta todo con PyInstaller.
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "==> Compilando frontend (Angular)" -ForegroundColor Cyan
Push-Location "$root\Frontend"
try {
    if (-not (Test-Path node_modules)) { npm ci; if ($LASTEXITCODE) { throw "npm ci ha fallado" } }
    npm run build -- --configuration production
    if ($LASTEXITCODE) { throw "El build de Angular ha fallado" }
} finally { Pop-Location }

Write-Host "==> Preparando entorno Python" -ForegroundColor Cyan
Push-Location "$root\Backend"
try {
    if (-not (Test-Path .venv)) { python -m venv .venv; if ($LASTEXITCODE) { throw "No se pudo crear el venv" } }
    $python = ".\.venv\Scripts\python.exe"
    & $python -m pip install --quiet -r requirements-desktop.txt
    if ($LASTEXITCODE) { throw "pip install ha fallado" }

    Write-Host "==> Empaquetando con PyInstaller" -ForegroundColor Cyan
    & $python -m PyInstaller guardias.spec --noconfirm --clean
    if ($LASTEXITCODE) { throw "PyInstaller ha fallado" }
} finally { Pop-Location }

Write-Host "==> Listo: $root\Backend\dist\Guardias.exe" -ForegroundColor Green
