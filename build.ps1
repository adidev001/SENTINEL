# build.ps1
Write-Host "Building SysSentinel AI Standalone Executable..."

# Activate Virtual Environment
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
    Write-Host "Virtual Environment Activated."
} else {
    Write-Host "Warning: .venv not found."
}
if (-Not (Test-Path ".\.venv\Scripts\flet.exe")) {
    Write-Host "Error: Flet not found in virtual environment."
    exit 1
}

# Run Flet Pack
# --noconsole: Hide terminal window
# --icon: Application icon
# --add-data: Bundle assets folder
# --name: Executable name
# --hidden-import: Ensure dynamic imports are caught (e.g. engine implementations)

# Clean previous builds to avoid overwrite prompt
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "SysSentinel.spec") { Remove-Item "SysSentinel.spec" -Force }

# Run Flet Pack
.\.venv\Scripts\flet.exe pack main.py `
    --name "SENTINEL" `
    --icon "assets/icon.ico" `
    --add-data "assets;assets" `
    --product-name "SysSentinel AI" `
    --product-version "1.0.0" `
    --copyright "Copyright (c) 2024 Devansh & Jahnavi" `
    --hidden-import "app.intelligence.local_ai" `
    --hidden-import "app.intelligence.cloud_ai" `
    --hidden-import "app.intelligence.rag_engine" `
    --hidden-import "sklearn.neighbors._partition_nodes" `
    --hidden-import "sklearn.utils._typedefs"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build Successful! Executable is in 'dist/SysSentinel.exe'"
} else {
    Write-Host "Build Failed."
}
