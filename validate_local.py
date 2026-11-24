"""Windows-friendly offline validation for LearnLens AI."""

import importlib.util
import subprocess
import sys
import urllib.request


def run(command):
    print(">", " ".join(command))
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)


def main():
    required_modules = ("streamlit", "pymupdf", "pptx", "faster_whisper")
    missing = [
        module for module in required_modules
        if importlib.util.find_spec(module) is None
    ]
    if missing:
        print("Missing Python modules:", ", ".join(missing))
        raise SystemExit(1)

    run([sys.executable, "-m", "py_compile", "app.py", "local_ai.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    run([sys.executable, "-m", "pip", "check"])

    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:11434/api/tags",
            timeout=3
        ) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
        print("Ollama: reachable on loopback")
    except Exception as error:
        print(f"Ollama: unavailable ({type(error).__name__})")
        print("Start Ollama before using local generation.")

    print("Local validation completed.")


if __name__ == "__main__":
    main()
