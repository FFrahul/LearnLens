# Windows Installation

## Prerequisites

- Windows PowerShell
- Python 3.10 or newer
- Ollama installed and running locally
- An installed Ollama text model (the default is `llama3.2:1b`)

## Setup

```powershell
cd "C:\Users\Dhruva kumar J\OneDrive\Desktop\AgenticAi(LearnSphere)"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
ollama list
```

If PowerShell execution policy blocks activation, use
`.venv\Scripts\python.exe -m pip ...` without activating the environment.
Install or pull model weights only when desired, for example
`ollama pull llama3.2:1b`. The repository does not require an API key.

## Configure

Keep `.env` local. Set `LEARNLENS_OLLAMA_MODEL` to a name shown by
`ollama list`. Optional settings include `llava:7b` for vision,
`LEARNLENS_WHISPER_MODEL` (`tiny` by default), GPU preference, SQLite path, and
profile ID. The Ollama host must remain loopback for a normal Windows run.

## Run and validate

```powershell
.\.venv\Scripts\python.exe validate_local.py
streamlit run app.py
```

Alternatively, `.\run_app.ps1` validates first and then starts Streamlit on
port 8501. Open `http://localhost:8501`.

## Optional Docker run

With Ollama still running on Windows:

```powershell
docker compose up --build
```

Compose connects the container to host Ollama through
`host.docker.internal:11434`. Override the app port with
`$env:LEARNLENS_PORT = "8502"` if 8501 is occupied. Containerized operation
requires Docker Desktop and is not required for the local Python setup.

## Troubleshooting

- Ollama unavailable: start Ollama and check `ollama list`.
- Model not installed: change `.env` to an installed model or explicitly pull
  the requested one.
- GPU Whisper failure: leave GPU enabled for automatic CPU fallback, or set
  `LEARNLENS_WHISPER_GPU=false`.
- PowerShell activation blocked: invoke the `.venv\Scripts\python.exe`
  executable directly.
