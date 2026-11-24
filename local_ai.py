"""Local-only Ollama inference and deterministic lexical feature hashing."""

import hashlib
import base64
import http.client
import json
import math
import os
import re
import urllib.parse
from dataclasses import dataclass


DEFAULT_MODEL = "llama3.2:1b"
DEFAULT_HOST = "http://127.0.0.1:11434"
EMBEDDING_DIMENSION = 768
_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "host.docker.internal"}


class LocalAIError(RuntimeError):
    """Raised when the configured local inference service is unavailable."""


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


def _validate_local_host(host):
    parsed = urllib.parse.urlsplit(host)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in _LOCAL_HOSTS
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Ollama must use a loopback HTTP address; remote inference is disabled."
        )
    return f"http://{parsed.netloc}"


def feature_hash_embedding(text, dimensions=EMBEDDING_DIMENSION):
    """Build a reproducible local lexical vector without model downloads."""
    if dimensions < 1:
        raise ValueError("dimensions must be positive")

    tokens = _TOKEN_PATTERN.findall(str(text).casefold())
    features = ["w:" + token for token in tokens]
    features.extend(
        "b:" + tokens[index] + " " + tokens[index + 1]
        for index in range(len(tokens) - 1)
    )
    vector = [0.0] * dimensions

    for feature in features:
        digest = hashlib.sha256(feature.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0 if digest[4] & 1 else -1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


class OllamaLocalAI:
    """Small Ollama client restricted to the local machine."""

    def __init__(self, model=None, host=None, timeout=90):
        self.model = (
            model
            or os.getenv("LEARNLENS_OLLAMA_MODEL")
            or DEFAULT_MODEL
        ).strip()
        self.host = _validate_local_host(
            host or os.getenv("OLLAMA_HOST", DEFAULT_HOST)
        )
        self.timeout = timeout

    def _request(self, path, payload=None, timeout=None):
        data = None
        headers = {}
        method = "GET"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
            method = "POST"

        parsed_host = urllib.parse.urlsplit(self.host)
        try:
            connection = http.client.HTTPConnection(
                parsed_host.hostname,
                parsed_host.port or 80,
                timeout=timeout or self.timeout
            )
            connection.request(
                method,
                path,
                body=data,
                headers=headers
            )
            response = connection.getresponse()
            body = response.read()
            if response.status < 200 or response.status >= 300:
                raise LocalAIError(
                    f"Ollama returned HTTP {response.status} for {path}."
                )
            return json.loads(body.decode("utf-8"))
        except LocalAIError:
            raise
        except (OSError, http.client.HTTPException) as error:
            raise LocalAIError(
                "Ollama is not reachable at "
                f"{self.host}. Start Ollama and try again."
            ) from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise LocalAIError(
                "Ollama returned an unreadable response."
            ) from error
        finally:
            if "connection" in locals():
                connection.close()

    def status(self):
        try:
            result = self._request("/api/tags", timeout=2)
        except LocalAIError as error:
            return {
                "available": False,
                "model_installed": False,
                "message": str(error)
            }

        installed = {
            entry.get("name")
            for entry in result.get("models", [])
            if isinstance(entry, dict)
        }
        model_installed = self.model in installed
        return {
            "available": True,
            "model_installed": model_installed,
            "installed_models": sorted(
                model for model in installed if model
            ),
            "message": (
                f"Local model ready: {self.model}"
                if model_installed
                else (
                    f"Ollama is running, but {self.model} is not installed. "
                    "Choose an already-installed model in .env or ask before "
                    "downloading another model."
                )
            )
        }

    def generate(self, prompt, json_mode=False):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 2048,
                "num_predict": 768,
                "temperature": 0.2
            }
        }
        if json_mode:
            payload["format"] = "json"

        result = self._request("/api/generate", payload=payload)
        response = result.get("response")
        if not isinstance(response, str) or not response.strip():
            raise LocalAIError("The local model returned an empty response.")
        return response.strip()

    def generate_with_image(self, prompt, image_bytes, mime_type):
        """Generate with a locally installed Ollama vision model."""
        vision_model = os.getenv(
            "LEARNLENS_OLLAMA_VISION_MODEL",
            "llava:7b"
        ).strip()
        payload = {
            "model": vision_model,
            "prompt": prompt,
            "images": [
                base64.b64encode(image_bytes).decode("ascii")
            ],
            "stream": False,
            "options": {
                "num_ctx": 2048,
                "num_predict": 512,
                "temperature": 0.2
            }
        }
        result = self._request("/api/generate", payload=payload)
        response = result.get("response")
        if not isinstance(response, str) or not response.strip():
            raise LocalAIError(
                f"Ollama vision model {vision_model} returned an empty response."
            )
        return response.strip()


class LocalVideoTranscriber:
    """Lazy-loaded Faster-Whisper transcription with local execution only."""

    def __init__(self, model_size=None, use_gpu=None):
        self.model_size = (
            model_size
            or os.getenv("LEARNLENS_WHISPER_MODEL")
            or "tiny"
        ).strip()
        configured_gpu = os.getenv(
            "LEARNLENS_WHISPER_GPU",
            "true"
        ).strip().casefold()
        self.use_gpu = (
            use_gpu
            if use_gpu is not None
            else configured_gpu in {"1", "true", "yes", "on"}
        )
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError as error:
            raise LocalAIError(
                "Local video transcription requires faster-whisper. "
                "Install the project requirements and retry."
            ) from error

        if self.use_gpu:
            try:
                self._model = WhisperModel(
                    self.model_size,
                    device="cuda",
                    compute_type="int8_float16"
                )
                return self._model
            except Exception:
                self._model = None

        try:
            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
                cpu_threads=int(
                    os.getenv("LEARNLENS_WHISPER_CPU_THREADS", "4")
                )
            )
        except Exception as error:
            raise LocalAIError(
                "The local transcription model could not start. "
                "Check available memory or disable GPU transcription with "
                "LEARNLENS_WHISPER_GPU=false."
            ) from error
        return self._model

    def transcribe(self, media_path):
        model = self._load_model()
        try:
            # PyAV 19 removed the metadata_errors keyword that older
            # Faster-Whisper releases still pass to av.open.
            import faster_whisper.audio as whisper_audio

            original_open = whisper_audio.av.open

            def compatible_open(*args, **kwargs):
                kwargs.pop("metadata_errors", None)
                return original_open(*args, **kwargs)

            whisper_audio.av.open = compatible_open
            beam_size = int(
                os.getenv("LEARNLENS_WHISPER_BEAM_SIZE", "1")
            )
            try:
                segments, _info = model.transcribe(
                    media_path,
                    vad_filter=True,
                    beam_size=beam_size
                )
            except RuntimeError as error:
                message = str(error).casefold()
                if not self.use_gpu or not any(
                    marker in message
                    for marker in ("cuda", "cublas", "cudnn")
                ):
                    raise
                self.use_gpu = False
                self._model = None
                model = self._load_model()
                segments, _info = model.transcribe(
                    media_path,
                    vad_filter=True,
                    beam_size=beam_size
                )
            return [
                TranscriptSegment(
                    start=float(segment.start),
                    end=float(segment.end),
                    text=str(segment.text).strip()
                )
                for segment in segments
                if str(segment.text).strip()
            ]
        except Exception as error:
            raise LocalAIError(
                "Local video transcription failed. Verify that FFmpeg can "
                "read this video and try a shorter clip."
            ) from error
        finally:
            if "whisper_audio" in locals():
                whisper_audio.av.open = original_open
