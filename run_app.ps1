$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Create .venv and install requirements first."
}

& $python validate_local.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $python -m streamlit run (Join-Path $PSScriptRoot "app.py") `
    --server.headless true `
    --server.port 8501
