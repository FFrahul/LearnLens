# Model Cards

## Default text model: `llama3.2:1b`

**Use:** local tutor answers, quiz generation and verification, grading,
knowledge tagging, and recovery text.  
**Runtime:** Ollama at `OLLAMA_HOST`; default is
`http://127.0.0.1:11434`.  
**Input:** retrieved extracted text and learner preferences.  
**Output:** grounded prose or structured JSON when requested.

The model is not bundled by this repository. It must already be installed with
Ollama or selected through `LEARNLENS_OLLAMA_MODEL`. Quality, latency, context
capacity, and memory use depend on the chosen model. The application adds
citations from retrieved sources when the model omits them, but this is not
sentence-level attribution.

## Optional vision model: `llava:7b`

**Use:** local image question answering through Ollama's base64 image payload.
It is optional and must be installed locally. A text-only Ollama installation
returns an actionable setup error; no remote image service is used.

## Video model: Faster-Whisper `tiny`

**Use:** local speech-to-text transcription with timestamped segments.  
**Configuration:** `LEARNLENS_WHISPER_MODEL`, GPU preference, beam size, and CPU
thread count are environment variables. CUDA is attempted when enabled and CPU
`int8` fallback is automatic.

The first use may download model weights. Transcription accuracy varies by
audio quality, language, and model size. Transcript results are cached locally
in SQLite.

## Retrieval representation: feature hashing

This is not a learned model. `feature_hash_embedding` hashes words and bigrams
into a normalized 768-dimensional vector. It avoids an embedding download and
is deterministic, but it does not provide the semantic understanding of a
modern embedding model. Unified retrieval supplements it with BM25-style
lexical matching.

## Experimental predictors

`sequence_experiment.py` provides optional local CPU DNN and LSTM baselines.
`experiment_readiness.py` blocks them until the required labeled observations
and topic coverage exist. Their output is exploratory and must not be presented
as validated learner prediction.
